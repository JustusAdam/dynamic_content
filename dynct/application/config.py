from pathlib import Path
import sys
from dynct.http import request
from dynct.http.server import ThreadedHTTPServer
from dynct.util.misc_decorators import singlecache

__author__ = 'justusadam'


_basedir = Path(__file__).parent.parent.resolve()


# add framework to pythonpath
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))


class ApplicationConfig:
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
    server_class = ThreadedHTTPServer
    http_request_handler = request.RequestHandler