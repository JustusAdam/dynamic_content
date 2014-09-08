from http.server import *
import os
from pathlib import Path

from pymysql import DatabaseError
from core.database import Database

from framework.config_tools import read_config
from includes import bootstrap
import core
from core import request_handler


os.chdir(str(Path(__file__).parent.resolve()))
__author__ = 'justusadam'


def main():
    try:
        db = Database()
        core.register_installed_modules(db)
        modules = core.load_modules(db)
        request_handler.hello = modules
    except DatabaseError as error:
        print('Failed to register installed modules, continuing.')
        print(error)
    finally:
        db = None

    request_handler.bootstrap = bootstrap

    run_server(handler_class=request_handler.RequestHandler)

    return 0


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    config = read_config('config')
    server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
