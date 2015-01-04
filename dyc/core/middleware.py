import inspect
import importlib
from . import component, get_component


__author__ = 'justusadam'


@component('Middleware')
class Container(object):
    def __init__(self):
        super().__init__()
        self.finalized = False
        self._wrapped = []

    def load(self, stuff):
        for item in stuff:
            package, name = item.rsplit('.', 1)
            module = importlib.import_module(package)
            obj = getattr(module, name)()
            if not isinstance(obj, Handler):
                raise TypeError
            self.register(obj)

    def finalize(self):
        self.finalized = True
        self._wrapped = tuple(self._wrapped)

    def register(self, obj, *options):
        if self.finalized:
            self._wrapped = self._wrapped + (obj, )
        self._wrapped.append(obj)

    def __getitem__(self, item):
        return self._wrapped[item]


class Handler(object):
    def handle_request(self, request):
        pass

    def handle_controller(self, request, handler, args, kwargs):
        pass

    def handle_view(self, request, view,  model):
        pass

    def handle_response(self, request, response_obj):
        pass


cmw = get_component('Middleware')


def register(options=(), args=(), kwargs={}):
    def _inner(cls):
        if inspect.isclass(cls) and issubclass(cls, Handler):
            cmw.register(cls(*args, **kwargs))
        elif isinstance(cls, Handler):
            cmw.register(cls)
        else:
            raise TypeError('Expected a subclass or instance of ' + repr(Handler))
        return cls
    if not args and not kwargs and (callable(options) or inspect.isclass(options)):
        return _inner(options)
    else:
        return _inner


register_as_middleware = register_middleware = register