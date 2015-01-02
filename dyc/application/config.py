import pathlib
import sys
from dyc.dchttp import server
from dyc.dchttp.request_handler import RequestHandler

__author__ = 'justusadam'

_basedir = pathlib.Path(__file__).parent.parent.resolve()


# add framework to pythonpath
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))


class ApplicationConfig(object):
    server_arguments = {}
    server_class = None
    http_request_handler = None
    basedir = _basedir

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


class DefaultConfig(ApplicationConfig):
    server_arguments = {
        "port": 8000,
        "host": ""
    }
    server_class = server.ThreadedHTTPServer
    http_request_handler = RequestHandler