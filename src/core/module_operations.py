from importlib import import_module
from pathlib import Path

from core import database_operations
from backend.database import DatabaseError
from includes import bootstrap
from application.config import ModuleConfig


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())


class ModuleError(Exception):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):
    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'


class ModuleController:
    def __init__(self, app, storage):
        self.base_app = app
        self.storage = storage

    def activate_module(self, module_name):
        print('Activating module: ' + module_name)
        if is_active(module_name):
            print('Module ' + module_name + ' is already active.')
            return True
        path = get_module_path(module_name)

        if path is None:
            print('Module ' + module_name + ' could not be activated')
            return False
        module = import_module(path.replace('/', '.'))

        return self._activate_module(module_name, module)


    def _activate_module(self, module_name, module):
        try:
            self.init_module(module)
        except DatabaseError as error:
            print(error)
            return False

        _set_module_active(module_name)
        return True

    def init_module(self, module):
        try:
            module.module_class(ModuleConfig(self.base_app, self.storage))
            module.setup_fragment()
        except ModuleError as error:
            print(error)
            print('it seems no setup_fragment() method could be found')

    def load_modules(self):
        modules = get_active_modules()
        for m in modules:
            if not hasattr(modules[m], 'module_class'):
                continue
            if hasattr(modules[m], 'default_config'):
                conf = modules[m].default_config(self, self.storage)
            else:
                conf = ModuleConfig(self, self.storage)
            yield m, modules[m].module_class(conf)

    def register_installed_modules(self):
        self.register_modules(self.discover_modules())

    def discover_modules(self):
        filename = '__init__.py'
        accumulator = []
        for directory in bootstrap.MODULES_DIRECTORIES + bootstrap.COREMODULES_DIRECTORIES:
            for file in Path(directory).iterdir():
                if file.is_dir():
                    configpath = file / filename
                    if configpath.exists():
                        accumulator.append(file)
        return accumulator

    def register_modules(self, r_modules):
        if isinstance(r_modules, (list, tuple)):
            for module in r_modules:
                self.register_single_module(module)
        else:
            self.register_single_module(r_modules)

    def register_single_module(self, module):
        assert isinstance(module, Path)
        print('registering module ' + module.name)
        db_op = database_operations.ModuleOperations()
        try:
            path = db_op.get_path(module.name)
            if path[0] != module.name:
                db_op.update_path(module.name, str(module))
        except (DatabaseError, TypeError):
            db_op.add_module(module.name, str(module), 'deprecated')


def register_content_handler(module_conf):
    print('registering content handler ' + module_conf['name'])
    if 'path_prefix' in module_conf:
        path_prefix = module_conf['path_prefix']
    else:
        path_prefix = module_conf['name']
    try:
        database_operations.ContentHandlers().add_new(module_conf['name'], module_conf['name'], path_prefix)
    except DatabaseError as error:
        print('Failed to register page handler ' + module_conf['name'])
        print(error)


def get_module_id(module_name):
    return database_operations.ModuleOperations().get_id(module_name)


def get_module_path(module):
    return database_operations.ModuleOperations().get_path(module)


def _set_module_active(module_name):
    database_operations.ModuleOperations().set_active(module_name)


def is_active(module_name):
    try:
        result = database_operations.ModuleOperations().ask_active(module_name)
    except DatabaseError:
        return False
    return result == 1

def check_info(info):
    keys = info.keys()
    necessary_attributes = bootstrap.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def get_active_modules():
    modules = {}
    for item in database_operations.ModuleOperations().get_enabled():
        print('loading module ' + item['name'])
        modules[item['name']] = import_module(item['path'].replace('/', '.'))
    return modules