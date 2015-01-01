import functools
from dyc.errors import exceptions

__author__ = 'justusadam'

_name_transform = lambda name: name.lower().replace('_', '').replace(' ', '')


def method_proxy(func):
    name = func if isinstance(func, str) else func.__name__
    def call(obj, *args, **kwargs):
        if obj._wrapped is None:
            raise exceptions.ComponentNotLoaded(obj._name)
        else:
            return getattr(obj._wrapped, name)(*args, **kwargs)
    return call if isinstance(func, str) else functools.wraps(func)(call)


class ComponentWrapper(object):
    _name = _wrapped = _allow_reload = None

    def __init__(self, name, allow_reload=False):
        self.__dict__['_name'] = name
        self.__dict__['_wrapped'] = None
        self.__dict__['_allow_reload'] = allow_reload

    def __getattr__(self, item):
        if self.__getattribute__('_wrapped') is None:
            raise exceptions.ComponentNotLoaded(item)
        return getattr(self._wrapped, item)

    def __setattr__(self, key, value):
        if key == '_wrapped':
            if self._wrapped is None:
                return super().__setattr__(key, value)
            elif self._allow_reload is False:
                raise exceptions.ComponentLoaded(self._name)
        else:
            setattr(self._wrapped, key, value)

    def __delattr__(self, item):
        if item is '_wrapped':
            raise TypeError('Cannot delete wrapped object')
        else:
            delattr(self._wrapped, item)

    def __call__(self, *args, **kwargs):
        return self._wrapped(*args, **kwargs)

    __dir__ = method_proxy('__dir__')
    __str__ = method_proxy('__str__')
    __setitem__ = method_proxy('__setitem__')
    __delitem__ = method_proxy('__delitem__')
    __getitem__ = method_proxy('__getitem__')


class ComponentContainer(dict):
    """
    Register Object for components.

    Dictionary with some special properties.

    Keys are transformed into all lower case and spaces and underscores are removed.

    => "_my Property" -> "myproperty"

    thus "_my Property" = "myproperty"

    """

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            raise AttributeError
        if len(args) == 1:
            if not kwargs:
                return self.__getitem__(args[0])
        return self.__getitem__(args[0])(*args[1:], **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = _name_transform(key)
        elif not isinstance(key, type):
            raise TypeError('Expected Type ' + repr(str) + ' or ' + repr(type) + ', got ' + repr(type(key)))
        item = super().setdefault(key, ComponentWrapper(key))
        item._wrapped = value

    def __getitem__(self, key):
        if isinstance(key, type):
            return self.classmap.setdefault(key, ComponentWrapper(key))
        else:
            new_key = _name_transform(key)
            return super().setdefault(new_key, ComponentWrapper(new_key))

    def __getattr__(self, item):
        return self.__getitem__(item)


call_component = get_component = ComponentContainer()


# removing the constructor for the accessor object
del ComponentContainer


def _decorator(name, *args, **kwargs):
    def inner(class_):
        register(name, class_(*args, **kwargs))
        return class_

    return inner


Component = component = _decorator


def register(name, obj):
    get_component[name] = obj


def inject_kwarg(component, argname):
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


def inject_arg(component):
    def inner(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            return func(get_component(component), *args, **kwargs)

        return wrap

    return inner