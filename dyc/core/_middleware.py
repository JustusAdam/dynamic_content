import inspect
from . import component, get_component

__author__ = 'justusadam'


@component('Middleware')
class Middleware(object):
    def __init__(self):
        super().__init__()
        self.request = []
        self.view = []
        self.response = []

    def finalize(self):
        self.request = tuple(self.request)
        self.view = tuple(self.view)
        self.response = tuple(self.response)

    def register(self, obj, options):
        if hasattr(obj, 'handle_request'):
            self.request.append(obj)
        if hasattr(obj, 'handle_view'):
            self.view.append(obj)
        if hasattr(obj, 'handle_response'):
            self.response.append(obj)

    def register_function(self, func, options):
        for attr in ('request', 'response', 'view'):
            if not options or attr in options:
                getattr(self, attr).append(func)

del Middleware

cmw = get_component('Middleware')


def middleware(options=(), args=(), kwargs={}):
    def _inner(func):
        if inspect.isclass(func):
            cmw.register(func(*args, **kwargs), options)
        elif callable(func):
            cmw.register_function(func, options)
        return func
    if not args and not kwargs and len(options) == 1 and (callable(options[0]) or inspect.isclass(options[0])):
        return _inner(options[0])
    else:
        return _inner


Middleware = middleware