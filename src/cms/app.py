import os

from application.app import Application
from backend.ar.base import VirtualDatabase
from core.module_operations import ModuleController
from backend.database import Database
from backend.connector import Connector
from modules.comp.decorator import Decorator
from application.moduleconnector import Modules
from core.urlparser import RequestMapper



__author__ = 'justusadam'


__http_request_parser_attribute_name = 'url_parser'


def _assign_http_request_parsers(modules, parser_container):
    assert isinstance(modules, dict)
    assert isinstance(parser_container, RequestMapper)
    for name in modules:
        if hasattr(modules[name], __http_request_parser_attribute_name):
            if getattr(modules[name], __http_request_parser_attribute_name):
                parser_container.register(getattr(modules[name], __http_request_parser_attribute_name))
    return parser_container



class MainApp(Application):
    _module_controller = None
    _url_parser = None

    def __init__(self, config):
        super().__init__(config)

    @property
    def module_controller(self):
        if not self._module_controller:
            self._module_controller = ModuleController(self, self.shell['v_storage'].connection)
        return self._module_controller

    @property
    def http_request_parser(self):
        if not self._url_parser:
            self._url_parser = RequestMapper(self.shell['v_storage'].connection)
        return self._url_parser

    @http_request_parser.setter
    def http_request_parser(self, value):
        assert isinstance(value, RequestMapper)
        self._url_parser = value

    def load(self):
        self.load_ar_database()
        self.register_modules()
        self.load_modules()
        self.assign_request_handlers()
        print('done')

    def assign_request_handlers(self):
        self.assign_http_request_handlers()

    def assign_http_request_handlers(self):
        self.http_request_parser = _assign_http_request_parsers(self.modules, self.http_request_parser)

    def run(self):
        self.run_http_server_loop()

    def run_http_server_loop(self):
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def handle_http_request(self, *args):
        def callback(url, post, client):
            request = self.http_request_parser(url, post)
            request.client = client
            print(request)
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