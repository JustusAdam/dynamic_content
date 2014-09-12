from importlib import import_module
from pathlib import Path
from framework.config_tools import read_config
from core.database import DatabaseError
from includes.bootstrap import Bootstrap
from .modules import Modules
from . import database_operations


__author__ = 'justusadam'


bootstrap = Bootstrap()

class ModuleError(Exception):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):

    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'


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

    return _activate_module(module_conf)


def _activate_module(module_conf):

    try:
        if 'required_tables' in module_conf:
            create_required_tables(module_conf['required_tables'])
        if 'insert' in module_conf:
            fill_tables(module_conf['insert'])
    except DatabaseError:
        return False

    known_roles = {
        'page_handler': register_content_handler
    }

    if module_conf['role'] in known_roles:
        known_roles[module_conf['role']](module_conf)

    _set_module_active(module_conf['name'])
    return True


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
    return database_operations.Modules().get_id(module_name)


def create_required_tables(tables):
    if isinstance(tables, (list, tuple)):
        database_operations.Modules().create_multiple_tables(*tables)
    else:
        database_operations.Modules().create_multiple_tables(tables)


def drop_module_tables(moduleconf):
    if 'required_tables' in moduleconf:
        print('dropping tables for ' + moduleconf['name'])
        try:
            database_operations.Modules().drop_tables(tuple(a['table_name'] for a in moduleconf['required_tables']))
        except DatabaseError as newerror:
            print('Could not drop table for ' + moduleconf['name'] + ' due to error: ' + str(
                newerror.args))


def fill_tables(values):
    database_operations.Modules().insert_into_tables(values)


def get_module_path(module):
    return database_operations.Modules().get_path(module)


def _set_module_active(module_name):
    database_operations.Modules().set_active(module_name)


def is_active(module_name):
    try:
        result = database_operations.Modules().ask_active(module_name)
    except DatabaseError:
        return False
    return result == 1


def register_installed_modules():
    register_modules(discover_modules())


def discover_modules():
    filename = bootstrap.MODULE_CONFIG_NAME
    accumulator = []
    for directory in (bootstrap.MODULES_DIRECTORY, bootstrap.COREMODULES_DIRECTORY):
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
        #print(','.join(list(a['name'] for a in r_modules)))
        for module in r_modules:
            register_single_module(module)
    else:
        register_single_module(r_modules)


def register_single_module(moduleconf):
    print('registering module ' + moduleconf['name'])
    db_op = database_operations.Modules()
    try:
        path = db_op.get_path(moduleconf['name'])
        if path[0] != moduleconf['path']:
            db_op.update_path(moduleconf['name'], moduleconf['path'])
    except (DatabaseError, TypeError):
        db_op.add_module(moduleconf['name'], moduleconf['path'], moduleconf['role'])


def check_info(info):
    keys = info.keys()
    necessary_attributes = bootstrap.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def load_active_modules():
    modules = {}
    for item in database_operations.Modules().get_enabled():
        print('loading module ' + item['name'])
        modules[item['name']] = import_module(item['path'].replace('/', '.'))

    a = Modules(modules)
    return a