"""
Main file that runs the application.
"""

from http.server import *
from pathlib import Path

from framework.tools.config import read_config
from core import request_handler
from framework.application.app import ApplicationConfig
from core.application import MainApp


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.resolve())


def main():
  c = read_config('config')
  config = ApplicationConfig()
  config.server_arguments = c['server_arguments']
  config.server_class = HTTPServer
  config.http_request_handler = request_handler.RequestHandler
  config.basedir = basedir

  app = MainApp(config)

  app.run()


if __name__ == '__main__':
  main()
