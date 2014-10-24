import os

from application.app import Application
from backend.ar.base import VirtualDatabase
from core.module_operations import ModuleController
from backend.database import Database
from backend.connector import Connector
from modules.comp.decorator import Decorator
from core.urlparser import RequestMapper
from application.moduleconnector import Modules



__author__ = 'justusadam'


class MainApp(Application):
    _module_controller = None

    def __init__(self, config):
        super().__init__(config)

    @property
    def module_controller(self):
        if not self._module_controller:
            self._module_controller = ModuleController(self, self.shell['v_storage'].connection)
        return self._module_controller

    def load(self):
        self.load_ar_database()
        self.register_modules()
        self.load_modules()

    def run(self):
        self.run_http_server_loop()

    def run_http_server_loop(self):
        self.http_request_parser = RequestMapper(self.shell['v_storage'].connection)
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def handle_http_request(self, *args):
        def callback(url, post, client):
            request = self.http_request_parser(url, post)
            request.client = client
            document = self.process_request(request)
            return document

        return self.config.http_request_handler(callback, *args)

    def legacy_handle_http_request(self, *args):
        def http_callback(url, client):
            return Decorator(url, client, '')

        return self.config.http_request_handler(http_callback, *args)

    def register_modules(self):
        self.module_controller.register_installed_modules()

    def load_modules(self):
        wrapper = Modules(ignore_overwrite=False)
        for name, _class in self.module_controller.load_modules():
            wrapper[name] = _class
        self.modules = wrapper

    def load_external(self, name, connection):
        self.shell[name] = Connector(name, connection)

    def load_ar_database(self):
        db = Database()
        ar = VirtualDatabase(db)
        self.load_external('v_storage', ar)

    def set_working_directory(self):
        os.chdir(self.config.basedir)

    def process_request(self, request):
        return self.decorate_response(self.create_view(request))

    def create_view(self, request):
        pass

    def decorate_response(self, response):
        return self.modules['comp'].basic_decorator(response)