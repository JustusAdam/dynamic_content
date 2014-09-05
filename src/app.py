from http.server import *
import os
from pathlib import Path

from pymysql import DatabaseError

from tools.config_tools import read_config


os.chdir(str(Path(__file__).parent.resolve()))

from includes.global_vars import *

__author__ = 'justusadam'


def main():
    try:
        roles['core'].register_installed_modules()
        roles['core'].load_modules()
    except DatabaseError as error:
        print('Failed to register installed modules, continuing.')
        print(error)

    run_server(handler_class=roles['core'].RequestHandler)

    return 0


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    config = read_config('config')
    server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
