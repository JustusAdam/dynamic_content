import os

from application.app import Application
from core.modules import Modules
from core.module_operations import register_installed_modules
from backend.database import Database
from backend.connector import Connector
from modules.comp.page_handler import BasicHandler


__author__ = 'justusadam'


class MainApp(Application):
    def __init__(self, config):
        super().__init__(config)

    def load(self):
        self.register_modules()
        self.load_modules()

    def run(self):
        self.run_http_server_loop()

    def run_http_server_loop(self):
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def handle_http_request(self, *args):
        def http_callback(url, client):
            return BasicHandler(url, client)

        return self.config.http_request_handler(http_callback, *args)

    def register_modules(self):
        register_installed_modules()

    def load_modules(self):
        self.modules = Modules()
        self.modules.reload()

    def set_working_directory(self):
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass