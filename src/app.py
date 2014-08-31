from http.server import *
from coremodules.olymp.request_handler import RequestHandler
from tools.config_tools import read_config
import os
from pathlib import Path


__author__ = 'justusadam'


def main():

    os.chdir(str(Path(__file__).parent.resolve()))

    run_server(handler_class=RequestHandler)

    return 0


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    config = read_config('config')
    server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
