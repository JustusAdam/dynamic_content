import os
from threading import Thread
from dynct.core import Modules
from dynct.core.mvc import controller_mapper

from dynct.core.mvc.model import Model
from dynct.modules.comp.template_formatter import TemplateFormatter
from dynct.util.typesafe import typesafe

from .config import ApplicationConfig, DefaultConfig

__author__ = 'justusadam'


class Application(Thread):
    """
    Main Application (should only be instantiated once) inherits from thread to release main thread for signal handling
     ergo Ctrl+C will almost immediately stop the application.

    call with .start() to execute in separate thread (recommended)

    call with .run() to execute in main thread (not recommended)
    """
    @typesafe
    def __init__(self, config:ApplicationConfig=DefaultConfig()):
        super().__init__()
        self.config = config
        self.load()

    def load(self):
        Modules.load()
        controller_mapper.sort()

    def run(self):
        self.run_http_server_loop()

    def load_modules(self):
        pass

    def handle_http_request(self, *args):
        def http_callback(url, client):
            model = Model()
            model.client = client
            model.view = controller_mapper(model, url)
            decorator = TemplateFormatter(model=model, url=url)
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