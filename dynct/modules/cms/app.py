import os

from dynct.application.app import Application
from dynct.modules.comp.decorator import DecoratorWithRegions
from dynct.core.mvc.controller import ControllerMapper


__author__ = 'justusadam'


class MainApp(Application):
    def __init__(self, config):
        super().__init__(config)

    def load(self):
        self.initialize_controller_mapper()

    def run(self):
        self.run_http_server_loop()

    def initialize_controller_mapper(self):
        self.controllers = ControllerMapper()
        self.controllers.register_modules()

    def run_http_server_loop(self):
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def handle_http_request(self, *args):
        def http_callback(url, client):
            model = self.controllers(url)(url, client)
            print(model.decorator_attributes)
            decorator = DecoratorWithRegions(model, url, client)
            print('')
            return decorator.compile_response()

        return self.config.http_request_handler(http_callback, *args)

    def set_working_directory(self):
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass