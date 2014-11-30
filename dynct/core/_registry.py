from pathlib import Path
from inspect import isclass

from .model import Module
from dynct.backend.database import Database
from dynct.util.config import read_config
from dynct.includes import settings
from dynct.core.model import ContentHandler
from dynct.util.module import import_by_path


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())

json_config_name = 'config.json'

python_config_name = 'module_config'


def get_module_conf(path:str):
    dir_ = Path(path)
    if dir_.is_dir() and json_config_name in dir_.iterdir():
        return read_config(str(dir_ / json_config_name))
    else:
        mod = import_by_path(path)
        if hasattr(mod, python_config_name):
            return getattr(mod, python_config_name)
    raise NotImplemented(path)


def activate_module(module_name):
    print('Activating module: ' + module_name)
    if is_active(module_name):
        print('Module ' + module_name + ' is already active.')
        return True
    path = get_module_path(module_name)

    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = get_module_conf('dynct/' + path)
    module_conf['path'] = path

    return _activate_module(module_conf)


def _activate_module(module_conf):
    try:
        init_module(module_conf)
    except IOError as error:
        print(error)
        return False

    _set_module_active(module_conf['name'])
    return True


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


def init_module(module_conf, force=False):
    if 'tables' in module_conf:
        db = Database
        for table, columns in module_conf['tables'].items():
            try:
                db.create_table(table, columns)
            except IOError as e:
                if force:
                    print('Encountered error: ' + repr(e))
                    print('Trying dropping table' + table)
                    db.drop_table(table)
                    db.create_table(table, columns)
                else:
                    raise e


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
    filename = settings.MODULE_CONFIG_NAME
    accumulator = []
    for directory in settings.MODULES_DIRECTORIES + settings.COREMODULES_DIRECTORIES:
        for file in Path(directory).iterdir():
            if file.is_dir():
                configpath = file / filename
                if configpath.exists():
                    info = read_config(str(configpath))
                    if check_info(info):
                        info['path'] = str(file)
                        accumulator.append(info)
    return accumulator


def register_modules(r_modules):
    if isinstance(r_modules, (list, tuple)):
        for module in r_modules:
            register_single_module(module)
    else:
        register_single_module(r_modules)


def register_single_module(moduleconf):
    assert isinstance(moduleconf, dict)
    print('registering module ' + moduleconf['name'])
    module = Module.get(module_name=moduleconf['name'])
    if module:
        if module.module_path != moduleconf['path']:
            module.module_path = moduleconf['path']
            module.save()
    else:
        Module(moduleconf['name'], moduleconf['path'], moduleconf['role']).save()


def check_info(info):
    keys = info.keys()
    necessary_attributes = settings.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def get_active_modules():
    return {item.module_name: import_by_path('dynct/' + item.module_path) for item in Module.get_all(enabled=True)}


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
        all_ = get_active_modules()
        for item in all_:
            dict.__setitem__(self, item, all_[item])
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