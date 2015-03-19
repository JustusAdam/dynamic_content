import functools
from framework import http
from framework.errors import exceptions

__author__ = 'Justus Adam'
__version__ = '0.1'


class Monad:
    def bind(self, func):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError


class Maybe(Monad):
    def __init__(self, content=None):
        self.content = content

    def get(self):
        return self.content

    def bind(self, func):
        if self.content is None:
            return self
        else:
            return func(self.content)


def catch_vardump(func):
    """
    Catch a vardump exception in func and return an error page containing the
    locals and globals of the function the exception was raised in

    :param func: wrapped function
    :return: wrapper function
    """
    def lformat(d):
        """
        Local formatting function transforming a dict into a string of <p> html
        elements containing the keys and values

        :param d: dict to format
        :return: html "formatted" str
        """
        return ''.join('<p>{}: {}</p>'.format(*a) for a in d.items())

    @functools.wraps(func)
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.Vardump as v:
            return http.response.Response(
                open('errors/error.html').read().format(
                    v.request, lformat(v.locals), lformat(v.globals)
                ).encode('utf-8'), code=200
            )
    return _inner
