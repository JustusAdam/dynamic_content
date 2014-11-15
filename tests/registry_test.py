import unittest
from dynct.modules.cms.app import MainApp
from dynct.application.config import ApplicationConfig
from dynct.core import Modules
from dynct.core.mvc.controller import Controller


__author__ = 'justusadam'


class RegistryTest(unittest.TestCase):

    def setUp(self):
        from dynct.modules.cms.main import basedir, config

        app_config = ApplicationConfig()
        app_config.server_arguments = config['server_arguments']
        app_config.basedir = basedir
        self.app = MainApp(app_config)
        self.app.load()

        self.controller = Modules

    def test_controller(self):
        print(self.app.controllers)
        print(self.controller.get_handlers_by_class(Controller))