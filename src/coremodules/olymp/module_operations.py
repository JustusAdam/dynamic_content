from tools.config_tools import read_config
from pathlib import Path
from .database import Database, escape, DatabaseError

__author__ = 'justusadam'


class ModuleError(Exception):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):

    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'


class Module:

    def __init__(self):
        self.bootstrap = read_config('includes/bootstrap')
        self.db = Database()
        self.is_setup = False

    def activate_module(self, module_name):
        #print('Activating module: ' + module_name)
        if not self.is_setup:
            if self.is_active(module_name):
                print('Module ' + module_name + ' is already active.')
                return True
            path = self.get_module_path(module_name)
        else:
            modules = self.discover_modules()
            path = None
            for module in modules:
                if module['name'] == module_name:
                    path = module['path']
                    break

        if path is None:
            print('Module ' + module_name + ' could not be activated')
            return False
        module_conf = read_config(path + '/config.json')

        try:
            if 'required_tables' in module_conf:
                self.create_required_tables(module_conf['required_tables'])
            if 'insert' in module_conf:
                self.fill_tables(module_conf['insert'])
        except DatabaseError:
            return False

        known_roles = {
            'page_handler': self.register_page_handler
        }

        if module_conf['role'] in known_roles:
            known_roles[module_conf['role']](module_conf)

        self._set_module_active(module_name)
        return True

    def register_page_handler(self, module_conf):
        print('registering page handler' + module_conf['name'])
        if 'path_prefix' in module_conf:
            path_prefix = module_conf['path_prefix']
        else:
            path_prefix = module_conf['name']
        try:
            self.db.insert('page_handlers', ['handler_module', 'handler_name', 'path_prefix'],
                           [self.get_module_id(module_conf['name']), module_conf['name'], path_prefix])
        except DatabaseError:
            print('Failed to register page handler')

    def get_module_id(self, module_name):
        db_result = self.db.select('id', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
        if not db_result is None:
            return db_result[0]
        raise ModuleNotFoundError

    def create_required_tables(self, tables):
        def create_table(table):
            try:
                self.db.create_table(**table)
            except DatabaseError:
                for column in table['columns']:
                    # RFE it would be nice to check beforehand instead of catching errors
                    try:
                        self.db.alter_table(table['table_name'], add=column)
                    except DatabaseError:
                        # TODO this might be dangerous, check if this breaks things (badly)
                        self.db.alter_table(table['table_name'], alter={column.split(' ', 1)[0]: column})

        if not isinstance(tables, (list, tuple)):
            tables = (tables,)
        for table in tables:
            create_table(table)

    def fill_tables(self, values):
        if not isinstance(values, (tuple, list)):
            values = (values,)
        for value in values:
            self.db.insert(**value)

    def get_module_path(self, module):
        query_result = self.db.select('module_path', 'modules', 'where module_name = ' + escape(module)).fetchone()
        if query_result is None:
            return None
        return query_result[0]

    def _set_module_active(self, module_name):
        if not self.is_active(module_name):
            self.db.update('modules', {'enabled': '1'}, 'module_name = ' + escape(module_name))

    def is_active(self, module_name):
        try:
            result = self.db.select('enabled', 'modules', 'where module_name = ' + escape(module_name)).fetchone()
        except DatabaseError:
            return False
        return result == 1

    def register_installed_modules(self):
        self.register_modules(self.discover_modules())

    def discover_modules(self):
        filename = self.bootstrap['MODULE_CONFIG_NAME']
        accumulator = []
        for directory in (self.bootstrap['MODULES_DIRECTORY'], self.bootstrap['COREMODULES_DIRECTORY']):
            for file in Path(directory).iterdir():
                if file.is_dir():
                    configpath = file / filename
                    if configpath.exists():
                        info = read_config(str(configpath))
                        if self.check_info(info):
                            info['path'] = str(file)
                            accumulator.append(info)
        return accumulator

    def register_modules(self, modules):
        if isinstance(modules, (list, tuple)):
            for module in modules:
                self.register_single_module(module)
        else:
            self.register_single_module(modules)

    def register_single_module(self, module):
        db_result = self.db.select('module_path', 'modules', 'where module_name=' + escape(module['name'])).fetchone()
        if db_result is None:
            self.db.insert('modules', ('module_name', 'module_path', 'module_role'), (module['name'], module['path'], module['role']))
        elif db_result[0] != module['path']:
            self.db.update('modules', {'module_path': module['path']}, 'module_name = ' + escape(module['name']))

    def check_info(self, info):
        keys = info.keys()
        necessary_attributes = self.bootstrap['NECESSARY_MODULE_ATTRIBUTES']
        for attr in necessary_attributes:
            if attr not in keys:
                return False
        return True