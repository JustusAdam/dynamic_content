import os
from tools.config_tools import read_config
from pathlib import Path
from .database import Database

__author__ = 'justusadam'


class Module:

    def __init__(self):
        self.bootstrap = read_config('includes/bootstrap')
        self.db = Database()

    def activate_module(self, module_name):
        path = self.get_module_path(module_name)

        module_conf = read_config(path.replace('.', '/') + '/config.json')
        operations = module_conf['database_queries']

        db_operations = {
            'create_table': self.db.create_table,
            'insert': self.db.insert,
            'update': self.db.update,
            'replace': self.db.replace
        }

        for operation in operations.keys():
            queries = operations[operation]
            if isinstance(queries, list) or isinstance(queries, tuple):
                for query in queries:
                    db_operations[operation](**query)
            else:
                db_operations[operation](**queries)


        self.db.update('modules', {'enabled': 'true'}, 'module_name = ' + module_name)

    def get_module_path(self, module):
        self.db.select('module_path', 'modules', 'where module_name = ' + module)

    def register_modules(self):

        for directory in (self.bootstrap['MODULES_DIRECTORY'], self.bootstrap['COREMODULES_DIRECTORY']):
            for file in Path(directory).iterdir():
                if file.is_dir():
                    infopath = file / 'info.json'
                    if infopath.exists():
                        info = read_config(file / 'info')
                        if self.check_info(info):
                            print(info)
                            self.register_module(str(file.resolve()), info)

    def register_module(self, path, info):
        self.db.replace('modules', ('module_name', 'module_path', 'module_role'), (info['name'], path, info['role']))

    def check_info(self, info):
        keys = info.keys()
        necessary_attributes = self.bootstrap['NECESSARY_MODULE_ATTRIBUTES']
        for attr in necessary_attributes:
            if attr not in keys:
                return False
        return True

    def get_installed_core_modules(self):
        modules = {}
        from importlib import import_module

        for module_directory in (self.bootstrap['MODULES_DIRECTORY'], self.bootstrap['COREMODULES_DIRECTORY']):
            for file in os.listdir(module_directory):
                try:
                    if file.endswith('.py'):
                        file = file[:-3]
                    file = module_directory + '.' + file
                    modules[import_module(file).name] = file
                except (ImportError, AttributeError) as err:
                    print(err)
                    pass
        return modules