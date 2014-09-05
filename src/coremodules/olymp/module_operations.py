from pathlib import Path

from tools.config_tools import read_config
from .database import escape, DatabaseError
from includes.global_vars import *


__author__ = 'justusadam'


class ModuleError(Exception):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):

    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'

_is_setup = False


def activate_module(module_name):
    #print('Activating module: ' + module_name)
    if not _is_setup:
        if is_active(module_name):
            print('Module ' + module_name + ' is already active.')
            return True
        path = get_module_path(module_name)
    else:
        d_modules = discover_modules()
        path = None
        for module in d_modules:
            if module['name'] == module_name:
                path = module['path']
                break

    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = read_config(path + '/config.json')

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

    _set_module_active(module_name)
    return True


def register_content_handler(module_conf):
    print('registering content handler ' + module_conf['name'])
    if 'path_prefix' in module_conf:
        path_prefix = module_conf['path_prefix']
    else:
        path_prefix = module_conf['name']
    try:
        db.replace('content_handlers', ['handler_module', 'handler_name', 'path_prefix'],
                       [get_module_id(module_conf['name']), module_conf['name'], path_prefix])
    except DatabaseError:
        print('Failed to register page handler ' + module_conf['name'])


def get_module_id(module_name):
    db_result = db.select('id', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
    if not db_result is None:
        return db_result[0]
    raise ModuleNotFoundError


def create_required_tables(tables):
    def create_table(t):
        try:
            db.create_table(**t)
        except DatabaseError:
            for column in t['columns']:
                # RFE it would be nice to check beforehand instead of catching errors
                try:
                    db.alter_table(t['table_name'], add=column)
                except DatabaseError:
                    # TODO this might be dangerous, check if this breaks things (badly)
                    db.alter_table(t['table_name'], alter={column.split(' ', 1)[0]: column})

    if not isinstance(tables, (list, tuple)):
        tables = (tables,)
    for table in tables:
        create_table(table)


def fill_tables(values):
    if not isinstance(values, (tuple, list)):
        values = (values,)
    for value in values:
        db.insert(**value)


def get_module_path(module):
    query_result = db.select('module_path', 'modules', 'where module_name = ' + escape(module)).fetchone()
    if query_result is None:
        return None
    return query_result[0]


def _set_module_active(module_name):
    if not is_active(module_name):
        db.update('modules', {'enabled': '1'}, 'module_name = ' + escape(module_name))


def is_active(module_name):
    try:
        result = db.select('enabled', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
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
        for module in r_modules:
            register_single_module(module)
    else:
        register_single_module(r_modules)


def register_single_module(module):
    db_result = db.select('module_path', 'modules', 'where module_name=' + escape(module['name'])).fetchone()
    if db_result is None:
        db.insert('modules', ('module_name', 'module_path', 'module_role'), (module['name'], module['path'], module['role']))
    elif db_result[0] != module['path']:
        db.update('modules', {'module_path': module['path']}, 'module_name = ' + escape(module['name']))


def check_info(info):
    keys = info.keys()
    necessary_attributes = bootstrap.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def load_active_modules():
    db_result = db.select(('module_name', 'module_path'), 'modules', 'where enabled = \'1\'')
    item = db_result.fetchone()
    while item:
        modules[item[0]] = import_module(item[1].replace('/', '.'))
        item = db_result.fetchone()
