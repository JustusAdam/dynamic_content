from http.server import *
import os
from pathlib import Path

from pymysql import DatabaseError

from framework.config_tools import read_config
import core
from core import request_handler
from framework.misc_decorators import requiredir


__author__ = 'justusadam'

basedir = str(Path(__file__).parent.resolve())

modules = None

os.chdir(basedir)


def main():
    try:
        core.register_installed_modules()
        global modules
        modules = core.load_modules()
    except DatabaseError as error:
        print('Failed to register installed modules, continuing.')
        print(error)

    run_server(handler_class=request_handler.RequestHandler)

    return 0


@requiredir(basedir)
def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    config = read_config('config')
    server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
