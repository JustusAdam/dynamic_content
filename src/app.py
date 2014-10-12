"""
Main file that runs the server.
"""

from http.server import *
import os
from pathlib import Path

from framework.shell.database import Database, DatabaseError
from framework.tools.config import read_config
import core
from core import request_handler
from framework.application.app import ApplicationConfig
from core.application import MainApp


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.resolve())

modules = None

os.chdir(basedir)


def main():
  try:
    db = Database()
    core.register_installed_modules()
    global modules
    modules = core.load_modules()
    db.close()
  except (core.dbo.DBOperationError, DatabaseError) as error:
    print('Failed to register installed modules, continuing.')
    print(error)

  run_server(server_class=HTTPServer, handler_class=request_handler.RequestHandler)

  return 0

def other_main():
  c = read_config('config')
  config = ApplicationConfig()
  config.server_arguments = c['server_arguments']
  config.server_class = HTTPServer
  config.http_request_handler = request_handler.RequestHandler

  app = MainApp(config)

  app.run()


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
  config = read_config('config')
  server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()


if __name__ == '__main__':
  other_main()
