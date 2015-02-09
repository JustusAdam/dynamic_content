import pathlib
import sys
from dynamic_content.util import structures
from dynamic_content.http import server
from dynamic_content.http import request_handler
from dynamic_content.http import wsgi


__author__ = 'Justus Adam'

__version__ = '0.1.1'

_basedir = pathlib.Path(__file__).parent.parent.resolve()


# add framework to pythonpath
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))


class ApplicationConfig(object):
    server_arguments = None
    server_class = None
    http_request_handler = None
    basedir = _basedir

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


class DefaultConfig(ApplicationConfig):
    server_arguments = structures.ServerArguments(
        port=8000,
        host="",
        ssl_port=9443
    )
    server_class = server.ThreadedHTTPServer
    http_request_handler = request_handler.RequestHandler
    wsgi_server = wsgi.Server
    wsgi_request_handler = wsgi.Handler
