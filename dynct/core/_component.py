import functools
from dynct.includes import log
from dynct.util import decorators

__author__ = 'justusadam'


_name_transform = decorators.transform_with(lambda name: name.lower().replace('_', '').replace(' ', ''))


class ComponentContainer(dict):
    """
    Register Object for components.

    Dictionary with some special properties.

    Keys are transformed into all lower case and spaces and underscores are removed.

    => "_my Property" -> "myproperty"

    thus "_my Property" = "myproperty"

    """
    def __init__(self):
        super().__init__()

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            raise AttributeError
        if len(args) == 1:
            if not kwargs:
                return self.__getitem__(args[0])
        return self.__getitem__(args[0])(*args[1:], **kwargs)

    @_name_transform('key', 1)
    def __setitem__(self, key, value):
        if key in self:
            message = ' '.join(["overwriting key", key, "of value", repr(super().__getitem__(key)), "with value", repr(value)])
            log.write_error(segment="ComponentContainer", message=message)
            print(message)
        return super().__setitem__(key, value)

    @_name_transform('key', 1)
    def __getitem__(self, key):
        return super().__getitem__(key)

    def __getattr__(self, item):
        return self.__getitem__(item)


call_component = get_component = ComponentContainer()


# removing the constructor for the accessor object
del ComponentContainer


def _decorator(name):
    def inner(class_, *args, **kwargs):
        register(name, class_(*args, **kwargs))
        return class_
    return inner



Component = component = _decorator


def register(name, obj):
    get_component[name] = obj


def inject(component, argname):
    """
    Inject a component when the function is called. (decorator)

    Component will be injected as keyword argument
    :param component:
    :param argname:
    :return:
    """
    def inner(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            kwargs[argname] = get_component(component)
            return func(*args, **kwargs)
        return wrap
    return inner