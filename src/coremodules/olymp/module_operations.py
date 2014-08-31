import os
from tools.config_tools import read_config
from pathlib import Path

__author__ = 'justusadam'


class Module:

    def __init__(self):
        self.bootstrap = read_config('includes/bootstrap')

    def activate_module(self,module):
        pass

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
        from .database import Database
        db = Database()
        db.replace('modules', ('module_name', 'module_path', 'module_role'), (info['name'], path, info['role']))

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