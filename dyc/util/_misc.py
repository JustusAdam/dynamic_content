import functools
from dyc import dchttp
from dyc.errors import exceptions

__author__ = 'Justus Adam'
__version__ = '0.1'


def catch_vardump(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.Vardump as v:
            return dchttp.response.Response(
                open('errors/error.html').read().format(
                    v.request, v.stacktrace, v.locals, v.globals
                ), code=200
            )
    return _inner