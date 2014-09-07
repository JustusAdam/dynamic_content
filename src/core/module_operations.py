from importlib import import_module
from pathlib import Path
from tools.config_tools import read_config
from core.database import escape, DatabaseError
from includes import bootstrap
from .modules import Modules


__author__ = 'justusadam'


class ModuleError(Exception):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):

    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'


def activate_module(module_name, db):
    print('Activating module: ' + module_name)
    if is_active(module_name, db):
        print('Module ' + module_name + ' is already active.')
        return True
    path = get_module_path(module_name, db)

    if path is None:
        print('Module ' + module_name + ' could not be activated')
        return False
    module_conf = read_config(path + '/config.json')

    return _activate_module(module_conf, db)


def _activate_module(module_conf, db):

    try:
        if 'required_tables' in module_conf:
            create_required_tables(module_conf['required_tables'], db)
        if 'insert' in module_conf:
            fill_tables(module_conf['insert'], db)
    except DatabaseError:
        return False

    known_roles = {
        'page_handler': register_content_handler
    }

    if module_conf['role'] in known_roles:
        known_roles[module_conf['role']](module_conf, db)

    _set_module_active(module_conf['name'], db)
    return True


def register_content_handler(module_conf, db):
    print('registering content handler ' + module_conf['name'])
    if 'path_prefix' in module_conf:
        path_prefix = module_conf['path_prefix']
    else:
        path_prefix = module_conf['name']
    try:
        db.replace('content_handlers', ('handler_module', 'handler_name', 'path_prefix'),
                   (module_conf['name'], module_conf['name'], path_prefix))
    except DatabaseError:
        print('Failed to register page handler ' + module_conf['name'])


def get_module_id(module_name, db):
    db_result = db.select('id', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
    if not db_result is None:
        return db_result[0]
    raise ModuleNotFoundError


def create_required_tables(tables, db):
    def create_table(t):
        try:
            db.create_table(**t)
        except DatabaseError as err:
            for column in t['columns']:
                print(err)
                # RFE it would be nice to check beforehand instead of catching errors
                try:
                    db.alter_table(t['table_name'], add=column)
                except DatabaseError as error:
                    print(error)
                    # TODO this might be dangerous, check if this breaks things (badly)
                    db.alter_table(t['table_name'], alter={column.split(' ', 1)[0]: column})

    if not isinstance(tables, (list, tuple)):
        tables = (tables,)
    for table in tables:
        create_table(table)


def drop_module_tables(moduleconf, db):
    if 'required_tables' in moduleconf:
        print('dropping tables for ' + moduleconf['name'])
        try:
            db.drop_tables(tuple(a['table_name'] for a in moduleconf['required_tables']))
        except DatabaseError as newerror:
            print('Could not drop table for ' + moduleconf['name'] + ' due to error: ' + str(
                newerror.args))


def fill_tables(values, db):
    if not isinstance(values, (tuple, list)):
        values = (values,)
    for value in values:
        db.insert(**value)


def get_module_path(module, db):
    query_result = db.select('module_path', 'modules', 'where module_name = ' + escape(module)).fetchone()
    if query_result is None:
        return None
    return query_result[0]


def _set_module_active(module_name, db):
    db.update('modules', {'enabled': '1'}, 'module_name = ' + escape(module_name))


def is_active(module_name, db):
    try:
        result = db.select('enabled', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
    except DatabaseError:
        return False
    return result == 1


def register_installed_modules(db):
    register_modules(discover_modules(), db)


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


def register_modules(r_modules, db):
    if isinstance(r_modules, (list, tuple)):
        #print(','.join(list(a['name'] for a in r_modules)))
        for module in r_modules:
            register_single_module(module, db)
    else:
        register_single_module(r_modules, db)


def register_single_module(moduleconf, db):
    #print('registering module ' + module['name'])
    db_result = db.select('module_path', 'modules', 'where module_name=' + escape(moduleconf['name'])).fetchone()
    if db_result is None:
        db.insert('modules', ('module_name', 'module_path', 'module_role'), (moduleconf['name'], moduleconf['path'], moduleconf['role']))
    elif db_result[0] != moduleconf['path']:
        db.update('modules', {'module_path': moduleconf['path']}, 'module_name = ' + escape(moduleconf['name']))


def check_info(info):
    keys = info.keys()
    necessary_attributes = bootstrap.NECESSARY_MODULE_ATTRIBUTES
    for attr in necessary_attributes:
        if attr not in keys:
            return False
    return True


def load_active_modules(db):
    db_result = db.select(('module_name', 'module_path'), 'modules', 'where enabled=' + escape(1))
    item = db_result.fetchone()
    modules = {}
    while item:
        print('loading module ' + item[0])
        modules[item[0]] = import_module(item[1].replace('/', '.'))
        item = db_result.fetchone()
    a = Modules(modules)
    return a