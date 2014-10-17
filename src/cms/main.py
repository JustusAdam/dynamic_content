"""
Main file that runs the application.
"""

from pathlib import Path
import os

from core.handlers import request
from core.handlers.server import ThreadedHTTPServer
from util.config import read_config
from application.app import ApplicationConfig
from cms.app import MainApp


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.parent.resolve())

os.chdir(basedir)


def main():
    config = read_config('cms/config')
    app_config = ApplicationConfig()
    app_config.server_arguments = config['server_arguments']
    app_config.server_class = ThreadedHTTPServer
    app_config.http_request_handler = request.RequestHandler
    app_config.basedir = basedir

    app = MainApp(app_config)

    app.run()


if __name__ == '__main__':
    main()
