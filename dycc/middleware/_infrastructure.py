import inspect
import importlib
import dycc
from dycc import hooks


__author__ = 'Justus Adam'
__version__ = '0.1'


class Handler(hooks.Hook):
    hook_name = 'middleware'

    def handle_request(self, request):
        pass

    def handle_controller(self, dc_obj, handler, args, kwargs):
        pass

    def handle_view(self, view, dc_obj):
        pass

    def handle_response(self, request, response_obj):
        pass


def load(stuff):
    for item in stuff:
        package, name = item.rsplit('.', 1)
        module = importlib.import_module(package)
        obj = getattr(module, name)()
        if not isinstance(obj, Handler):
            raise TypeError
        obj.register_instance()


Handler.init_hook()


cmw = dycc.get_component('Middleware')


def register(options=(), args=(), kwargs=None):

    kwargs = kwargs if not kwargs is None else {}
    def _inner(cls):
        if inspect.isclass(cls) and issubclass(cls, Handler):
            instance = cls(*args, **kwargs)
        elif isinstance(cls, Handler):
            instance = cls
        else:
            raise TypeError(
                'Expected a subclass or instance of {}, got {}'.format(
                    Handler, type(cls)
                    )
                )
        instance.register_instance()
        return cls
    if not args and not kwargs and (callable(options)
                                    or inspect.isclass(options)):
        return _inner(options)
    else:
        return _inner


register_as_middleware = register_middleware = register
