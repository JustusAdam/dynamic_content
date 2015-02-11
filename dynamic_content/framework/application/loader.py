import importlib
from framework import middleware
from framework import component
from framework.includes import log
from framework.util import console, structures

__author__ = 'Justus Adam'
__version__ = '0.1'


class Loader:
    @component.inject_method('settings')
    def __init__(self, settings, init_function=None):
        self.settings = settings
        self.init_function = init_function

    def load(self):
        if self.settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('loading components')
        console.print_info('Loading Components ... ')
        from framework import mvc, route, dchp
        console.print_info('Loading Middleware ...')
        middleware.load(self.settings['middleware'])
        console.print_info('Loading Modules ...')
        self.load_modules()
        if callable(self.init_function):
            self.init_function()
        self.load_apps()

    def load_modules(self):
        """
        Load modules specified in settings

        :return: None
        """
        for module in self.settings['modules']:
            importlib.import_module('.' + module, 'dycm')

    def load_apps(self):
        """
        Load apps

        :return: None
        """
        for module in self.settings['import']:
            importlib.import_module(module)