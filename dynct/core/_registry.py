import inspect
from pathlib import Path
from inspect import isclass
from dynct.backend.orm import BaseModel

from .model import Module
from dynct.util.config import read_config
from dynct.includes import settings
from dynct.core.model import ContentHandler
from dynct.util.module import import_by_path
from dynct.includes import log


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())

json_config_name = 'config.json'

python_config_name = 'module_config'


def get_module_conf(path:str, module):
    dir_ = Path(path)
    if dir_.is_dir() and json_config_name in dir_.iterdir():
        return read_config(str(dir_ / json_config_name))
    else:
        if hasattr(module, python_config_name):
            return getattr(module, python_config_name)
    raise NotImplemented(path)


def activate_module(module_name):
    print('Activating module: ' + module_name)
    if is_active(module_name):
        print('Module ' + module_name + ' is already active.')
        return True
    path = get_module_path(module_name)
    module = import_by_path('dynct/' + path)
    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = get_module_conf('dynct/' + path, module)
    module_conf['path'] = path
    init_tables(module)
    return _set_module_active(module_conf['name'])


def init_tables(m):
    for item in dir(m):
        item = getattr(m, item)
        if inspect.isclass(item) and issubclass(item, BaseModel):
            try:
                item.create_table()
            except Exception as e:
                print(e)
                log.write_error(function='create_table', message=str(e))


def register_content_handler(module_conf):
    print('registering content handler ' + module_conf['name'])
    if 'path_prefix' in module_conf:
        path_prefix = module_conf['path_prefix']
    else:
        path_prefix = module_conf['name']
    try:
        ContentHandler(module_conf['name'], module_conf['name'], path_prefix).save()
    except IOError as error:
        print('Failed to register page handler ' + module_conf['name'])
        print(error)


def get_module_id(module_name):
    return Module.get(module_name=module_name).id


def get_module_path(module):
    return Module.get(module_name=module).module_path


def _set_module_active(module_name):
    a = Module.get(module_name=module_name)
    a.enabled = True
    a.save()


def is_active(module_name):
    result = Module.get(module_name=module_name)
    if result:
        return bool(result.enabled)
    else:
        return False


def register_installed_modules():
    register_modules(discover_modules())


def discover_modules():
    for directory in settings.MODULES_DIRECTORIES + settings.COREMODULES_DIRECTORIES:
        for file in Path(directory).iterdir():
            yield {
                'name': str(file.name),
                'path': str(file)
            }


def register_modules(r_modules):
    if isinstance(r_modules, (list, tuple)):
        for module in r_modules:
            register_single_module(module)
    else:
        register_single_module(r_modules)


def register_single_module(moduleconf):
    assert isinstance(moduleconf, dict)
    print('registering module ' + moduleconf['name'])
    module = Module.get(machine_name=moduleconf['name'])
    if module:
        if module.module_path != moduleconf['path']:
            module.module_path = moduleconf['path']
            module.save()
    else:
        Module.create(machine_name=moduleconf['name'], path=moduleconf['path'])


def check_info(info):
    keys = info.keys()
    necessary_attributes = settings.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def get_active_modules():
    try:
        modules = Module.select().where(Module.enabled==True)
        return {item.machine_name: import_by_path('dynct/' + item.path) for item in modules}
    except Exception:
        def find(name, paths):
            for path in paths:
                for file in Path(path).iterdir():
                    if file.name == name: return str(file)
            else:
                raise FileNotFoundError('default module ' + name + ' is missing')
        return {i: import_by_path('dynct/' + find(i, settings.MODULES_DIRECTORIES)) for i in settings.DEFAULT_MODULES}


def ensure_loaded(func):
    def wrap(instance, *args, **kwargs):
        if not instance.loaded:
            instance.load()
        return func(instance, *args, **kwargs)
    return wrap


class Modules(dict):
    """
    Immutable Module dictionary.
    """

    def __init__(self):
        super().__init__()
        self.loaded = False

    def reload(self):
        self.load()

    def load(self):
        from dynct import core
        all_ = get_active_modules()
        all_['core'] = core
        for name, value in all_.items():
            dict.__setitem__(self, name, value)
        self.loaded = True

    def __getitem__(self, key):
        if not self.loaded:
            self.load()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        raise PermissionError

    @ensure_loaded
    def _get_handlers(self, func, single_value):
        acc = {}

        def add(key, value):
            if single_value:
                acc[key] = value
            elif key in acc:
                acc[key].append(value)
            else:
                acc[key] = [value]

        for a in self:
            for b in filter(lambda s: not s.startswith('_'), self[a].__dict__.keys()):
                if func(b, getattr(self[a], b)):
                    add(a, getattr(self[a], b))
        return acc

    def get_handlers_by_class(self, class_, single_value=False):
        return self._get_handlers(
            lambda a, b: isclass(b) and issubclass(b, class_), single_value
        )

    def get_handlers_by_name(self, name:str, single_value=False):
        if name.startswith('_'):
            raise TypeError('name', 'identifier on non-hidden attribute (does not start with \'_\')')
        return self._get_handlers(
            lambda a, b: b == name, single_value
        )

    def __str__(self):
        if not self.loaded:
            self.load()
        return super().__str__()