from framework.application import Application
from .modules import Modules
from .module_operations import register_installed_modules
from framework.shell.database import Database
from framework.shell.connector import Connector
import os

__author__ = 'justusadam'


class MainApp(Application):

  def __init__(self, config):
    super().__init__(config)

  def load(self):
    self.register_modules()
    self.load_modules()
    self.load_database()

  def run(self):
    self.run_http_server_loop()

  def run_http_server_loop(self):
    server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
    httpd = self.config.server_class(server_address, self.handle_http_request)
    httpd.serve_forever()

  def handle_http_request(self, *args):
    return self.config.http_request_handler(*args)

  def register_modules(self):
    register_installed_modules()

  def load_modules(self):
    self.modules = Modules()
    self.modules.reload()

  def load_external(self, name, connection):
    self.shell[name] = Connector(name, connection)

  def load_database(self):
    self.load_external('database', Database())

  def set_working_directory(self):
    os.chdir(self.config.basedir)