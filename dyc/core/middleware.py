import inspect
from . import component, get_component

__author__ = 'justusadam'


@component('Middleware')
class Container(object):
    def __init__(self):
        super().__init__()
        self.finalized = False
        self._wrapped = []

    def finalize(self):
        self.finalized = True
        self._wrapped = tuple(self._wrapped)

    def register(self, obj, options):
        if self.finalized:
            self._wrapped = self._wrapped + (obj, )
        self._wrapped.append(obj)


class Handler(object):
    def handle_request(self, request):
        pass

    def handle_view(self, request, handler, args, kwargs):
        pass

    def handle_response(self, request, view,  model):
        pass


cmw = get_component('Middleware')


def middleware(options=(), args=(), kwargs={}):
    def _inner(cls):
        if inspect.isclass(cls) and issubclass(cls, Handler):
            cmw.register(cls(*args, **kwargs))
        elif isinstance(cls, Handler):
            cmw.register(cls)
        else:
            raise TypeError('Expected a subclass or instance of ' + repr(Handler))
    if not args and not kwargs and len(options) == 1 and (callable(options[0]) or inspect.isclass(options[0])):
        return _inner(options[0])
    else:
        return _inner


register = register_as_middleware = register_middleware = middleware