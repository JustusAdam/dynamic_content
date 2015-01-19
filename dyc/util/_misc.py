import functools
from dyc import dchttp
from dyc.errors import exceptions

__author__ = 'Justus Adam'
__version__ = '0.1'


def catch_vardump(func):
    def lformat(d):
        return ''.join('<p>{}: {}</p>'.format(*a) for a in d.items())

    @functools.wraps(func)
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.Vardump as v:
            return dchttp.response.Response(
                open('errors/error.html').read().format(
                    v.request, lformat(v.locals), lformat(v.globals)
                ).encode('utf-8'), code=200
            )
    return _inner