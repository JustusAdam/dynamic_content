"""
Main file that runs the application.
"""

from pathlib import Path

from core.handlers import request
from core.handlers.server import ThreadedHTTPServer

from util.config import read_config
from application.app import ApplicationConfig
from cms.application import MainApp


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.resolve())


def main():
  c = read_config('config')
  config = ApplicationConfig()
  config.server_arguments = c['server_arguments']
  config.server_class = ThreadedHTTPServer
  config.http_request_handler = request.RequestHandler
  config.basedir = basedir

  app = MainApp(config)

  app.run()


if __name__ == '__main__':
  main()
