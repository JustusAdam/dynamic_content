import os
from .config import ApplicationConfig, DefaultConfig
from dynct.core.mvc.controller import ControllerMapper
from dynct.core.mvc.model import Model
from dynct.modules.comp.template_formatter import TemplateFormatter
from dynct.util.typesafe import typesafe

__author__ = 'justusadam'


class Application(object):
    @typesafe
    def __init__(self, config:ApplicationConfig=DefaultConfig()):
        self.config = config
        self.load()

    def load(self):
        self.initialize_controller_mapper()

    def run(self):
        self.run_http_server_loop()

    def load_modules(self):
        pass

    def initialize_controller_mapper(self):
        self.controllers = ControllerMapper()
        self.controllers.register_modules()

    def handle_http_request(self, *args):
        def http_callback(url, client):
            model = Model()
            model.client = client
            model.view = self.controllers(url)(model, url)
            decorator = TemplateFormatter(model, url)
            return decorator.compile_response()

        return self.config.http_request_handler(http_callback, *args)

    def run_http_server_loop(self):
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def set_working_directory(self):
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass