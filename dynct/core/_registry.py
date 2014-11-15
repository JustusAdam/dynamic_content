from importlib import import_module
from pathlib import Path
from inspect import isclass

from dynct.backend.ar import ARObject
from dynct.errors import ModuleError, DatabaseError, InvalidInputError
from dynct.errors.exceptions import OverwriteProhibitedError
from dynct.util.config import read_config
from dynct.includes import bootstrap
from dynct.core.ar import ContentHandler


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())


class Module(ARObject):
    _table = 'modules'

    def __init__(self, module_name, module_path, module_role, enabled=False, id=-1):
        self.module_name = module_name
        self.module_path = module_path
        self.module_role = module_role
        self.id = id
        self.enabled = enabled



def activate_module(module_name):
    print('Activating module: ' + module_name)
    if is_active(module_name):
        print('Module ' + module_name + ' is already active.')
        return True
    path = get_module_path(module_name)

    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = read_config(path + '/config.json')
    module_conf['path'] = path

    return _activate_module(module_conf)


def _activate_module(module_conf):
    try:
        init_module(module_conf['path'])
    except DatabaseError as error:
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
    except DatabaseError as error:
        print('Failed to register page handler ' + module_conf['name'])
        print(error)


def get_module_id(module_name):
    return Module.get(module_name=module_name).id


def init_module(module_path):
    module = import_module(module_path.replace('/', '.'))
    try:
        module.prepare()
    except ModuleError as error:
        print(error)
        print('it seems no prepare() method could be found')


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
    filename = bootstrap.MODULE_CONFIG_NAME
    accumulator = []
    for directory in bootstrap.MODULES_DIRECTORIES + bootstrap.COREMODULES_DIRECTORIES:
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
    necessary_attributes = bootstrap.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def get_active_modules():
    return {item.module_name: import_module('dynct.' + item.module_path.replace('/', '.')) for item in Module.get_all(enabled=True)}


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
        raise OverwriteProhibitedError

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
            raise InvalidInputError('name', 'identifier on non-hidden attribute (does not start with \'_\')')
        return self._get_handlers(
            lambda a, b: b == name, single_value
        )

    def __str__(self):
        if not self.loaded:
            self.load()
        return super().__str__()