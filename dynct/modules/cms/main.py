"""
Main file that runs the application.
"""

from pathlib import Path
import os
import sys


# ensure the correct directory is used
from dynct.http import request

basedir = Path(__file__).parent.parent.parent.resolve()
os.chdir(str(basedir))
#add framework to pythonpath
if not str(basedir.parent) in sys.path:
    sys.path.append(str(basedir.parent))

from dynct.http.server import ThreadedHTTPServer
from dynct.util.config import read_config
from dynct.application.app import ApplicationConfig
from dynct.modules.cms.app import MainApp

config = read_config('modules/cms/config')

__author__ = 'justusadam'


def main():
    app_config = ApplicationConfig()
    app_config.server_arguments = config['server_arguments']
    app_config.server_class = ThreadedHTTPServer
    app_config.http_request_handler = request.RequestHandler
    app_config.basedir = basedir

    app = MainApp(app_config)

    app.run()


if __name__ == '__main__':
    main()
