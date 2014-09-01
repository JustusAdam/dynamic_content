import os
from pymysql import DatabaseError
from tools.config_tools import read_config
from pathlib import Path
from .database import Database, escape

__author__ = 'justusadam'


class Module:

    def __init__(self):
        self.bootstrap = read_config('includes/bootstrap')
        self.db = Database()
        self.is_setup = False

    def activate_module(self, module_name):
        print('Activating module: ' + module_name)
        if not self.is_setup:
            if self.is_active(module_name):
                return False
            path = self.get_module_path(module_name)
        else:
            modules = self.discover_modules()
            path = ''
            for module in modules:
                if module['name'] == module_name:
                    path = module['path']
                    break

        module_conf = read_config(path + '/config.json')

        for table in module_conf['required_tables']:
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

        self.db.update('modules', {'enabled': 'true'}, 'module_name = ' + escape(module_name))
        return True

    def get_module_path(self, module):
        return self.db.select('module_path', 'modules', 'where module_name = ' + escape(module)).fetchone()

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
        if isinstance(modules, list) or isinstance(modules, tuple):
            for module in modules:
                self.register_single_module(module)
        else:
            self.register_single_module(modules)


    def register_single_module(self, module):
        db_result = self.db.select('module_path', 'modules', 'where module_name=' + escape(module['name'])).fetchone()[0]
        if db_result is None:
            self.db.insert('modules', ('module_name', 'module_path', 'module_role'), (module['name'], module['path'], module['role']))
        elif db_result != module['path']:
            self.db.update('modules', {'module_path': module['path']}, 'where module_name = ' + escape(module['name']))

    def check_info(self, info):
        keys = info.keys()
        necessary_attributes = self.bootstrap['NECESSARY_MODULE_ATTRIBUTES']
        for attr in necessary_attributes:
            if attr not in keys:
                return False
        return True