"""
Main file that runs the application.
"""

from pathlib import Path

from core.handlers import request
from core.handlers.server import ThreadedHTTPServer

from util.config import read_config
from application.app import ApplicationConfig
from cms.app import MainApp
import os


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())

os.chdir(basedir)

def main():
  c = read_config('cms/config')
  config = ApplicationConfig()
  config.server_arguments = c['server_arguments']
  config.server_class = ThreadedHTTPServer
  config.http_request_handler = request.RequestHandler
  config.basedir = basedir

  app = MainApp(config)

  app.run()


if __name__ == '__main__':
  main()
