import pathlib
import inspect
from dyc.backend import orm

from . import model, Component
from dyc.util import config, lazy
from dyc.includes import settings
from dyc.core import model as coremodel
from dyc.util import module as _module
from dyc.includes import log


__author__ = 'justusadam'

basedir = str(pathlib.Path(__file__).parent.parent.resolve())

json_config_name = 'config.json'

python_config_name = 'module_config'


def get_module_conf(path:str, module):
    dir_ = pathlib.Path(path)
    if dir_.is_dir() and json_config_name in dir_.iterdir():
        return config.read_config(str(dir_ / json_config_name))
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
    m = _module.import_by_path('dyc/' + path)
    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = get_module_conf('dyc/' + path, m)
    module_conf['path'] = path
    init_tables(m)
    return _set_module_active(module_conf['name'])


def init_tables(m):
    for item in dir(m):
        item = getattr(m, item)
        if inspect.isclass(item) and issubclass(item, orm.BaseModel):
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
        coremodel.ContentHandler(module_conf['name'], module_conf['name'], path_prefix).save()
    except IOError as error:
        print('Failed to register page handler ' + module_conf['name'])
        print(error)


def get_module_id(module_name):
    return model.Module.get(machine_name=module_name).id


def get_module_path(module):
    return model.Module.get(machine_name=module).module_path


def _set_module_active(module_name):
    a = model.Module.get(machine_name=module_name)
    a.enabled = True
    a.save()


def is_active(module_name):
    result = model.Module.get(module_name=module_name)
    if result:
        return bool(result.enabled)
    else:
        return False


def register_installed_modules():
    register_modules(discover_modules())


def discover_modules():
    for directory in settings.MODULES_DIRECTORIES + settings.COREMODULES_DIRECTORIES:
        for file in filter(lambda s: (s.is_dir() or s.suffix == '.py') and not s.name.startswith('_'),
                           pathlib.Path(directory).iterdir()):
            yield {
                'name': str(file.stem),
                'path': str(file)
            }


def register_modules(r_modules):
    if isinstance(r_modules, dict):
        register_single_module(r_modules)
    elif hasattr(r_modules, '__iter__'):
        for module in r_modules:
            register_single_module(module)
    else:
        raise ValueError


def register_single_module(moduleconf):
    assert isinstance(moduleconf, dict)
    print('registering module ' + moduleconf['name'])
    module = model.Module.select().where(model.Module.machine_name == moduleconf['name'])
    if module.wrapped_count():
        module = module[0]
        if module.path != moduleconf['path']:
            module.path = moduleconf['path']
            module.save()
    else:
        model.Module.create(machine_name=moduleconf['name'], path=moduleconf['path'])


def check_info(info):
    keys = info.keys()
    necessary_attributes = settings.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def get_active_modules():
    modules = model.Module.select().where(model.Module.enabled == True)
    return {item.machine_name: _module.import_by_path('dyc/' + item.path) for item in modules}


@Component("Modules")
class Modules(dict, lazy.Loadable):
    """
    Immutable Module dictionary.
    """

    def __init__(self):
        super().__init__()

    def reload(self):
        self.load()

    def load(self):
        register_installed_modules()
        all_ = get_active_modules()
        # from dyc import core
        # all_['core'] = core
        for name, value in all_.items():
            dict.__setitem__(self, name, value)
        self.loaded = True

    @lazy.ensure_loaded
    def __getitem__(self, key):
        if isinstance(key, model.Module):
            key = key.machine_name
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        raise PermissionError

    @lazy.ensure_loaded
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

    @lazy.ensure_loaded
    def get_handlers_by_class(self, class_, single_value=False):
        return self._get_handlers(
            lambda a, b: inspect.isclass(b) and issubclass(b, class_), single_value
        )

    @lazy.ensure_loaded
    def get_handlers_by_name(self, name:str, single_value=False):
        if name.startswith('_'):
            raise TypeError('name', 'identifier on non-hidden attribute (does not start with \'_\')')
        return self._get_handlers(
            lambda a, b: b == name, single_value
        )

    @lazy.ensure_loaded
    def __str__(self):
        return super().__str__()