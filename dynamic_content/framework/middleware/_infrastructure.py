"""Basic infrastructure for middleware"""
import inspect
import importlib
from framework import hooks
from framework.machinery import component


__author__ = 'Justus Adam'
__version__ = '0.1'


class Handler(hooks.ClassHook):
    """
    Middleware handler/hook base class

    Flyweight object by default
    """
    __slots__ = ()

    hook_name = 'middleware'

    def handle_request(self, request):
        """
        Method to be overwritten when hooking right after the request creation

        :param request:
        :return:
        """
        pass

    def handle_controller(self, dc_obj, handler, args, kwargs):
        """
        Method to overwrite when hooking after the controller resolving

        :param dc_obj:
        :param handler:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def handle_view(self, view, dc_obj):
        """
        Method to overwrite when hooking after/if controller ran

        :param view:
        :param dc_obj:
        :return:
        """
        pass

    def handle_response(self, request, response_obj):
        """
        Method to overwrite when hooking after response creation

        :param request:
        :param response_obj:
        :return:
        """
        pass


def load(stuff):
    """
    Load all classes in stuff

    :param stuff: iterable of strings
    :return: None
    """
    for item in stuff:
        package, name = item.rsplit('.', 1)
        module = importlib.import_module(package)
        obj = getattr(module, name)()
        if not isinstance(obj, Handler):
            raise TypeError
        obj.register_instance()


Handler.init_hook()


@component.inject('middleware')
def get_middleware(middleware):
    """
    Convenience method for retrieving the middleware component

    :param middleware: injected component
    :return: middleware component
    """
    return middleware


def register(options=(), args=(), kwargs=None):
    """
    Register decorated class as middleware, instantiating with args, kwargs

    :param options:
    :param args:
    :param kwargs:
    :return: wrapper function or class
    """

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
