from framework import middleware
import logging
from framework.machinery import component, registry, scanner

__author__ = 'Justus Adam'
__version__ = '0.1'


class Loader:
    @component.inject_method('settings')
    def __init__(self, settings, init_function=None):
        self.settings = settings
        self.init_function = init_function
        self.registry = registry.Registry()
        self.scanner_instance = scanner.Scanner()

    def load(self):
        """
        Main work of the loader
        :return: None
        """
        logging.info('Loading Components ... ')
        from framework import mvc, route, dchp
        logging.warning('Loading Middleware ...')
        middleware.load(self.settings['middleware'])
        logging.info('Loading Modules ...')
        self.run_scanner()
        if callable(self.init_function):
            self.init_function()

    def run_scanner(self):
        """
        Runs the Scanner

        :return: None
        """
        self.scanner_instance.scan_from_settings()