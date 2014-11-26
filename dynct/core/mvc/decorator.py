from collections import ChainMap
from functools import wraps

from . import Config, DefaultConfig
import re
from .controller import Controller, controller_mapper
from .model import Model
from dynct.util.misc_decorators import apply_to_type
from dynct.util.typesafe import typesafe

__author__ = 'justusadam'


class Autoconf:
    """
    Chains Custom config, model config and default conf and assigns it to the model.

    Priority is given as follows:
     Model.config > custom config argument? > Controller.config? > DefaultConfig
     ? is optional, will be omitted if bool(?) == false
    """
    @typesafe
    def __init__(self, conf:Config=None):
        self.custom_conf = conf

    def __call__(self, func):
        @wraps(func)
        @apply_to_type(Model, Controller)
        def wrap(model, controller):
            model.config = ChainMap(*[a for a in [
                model.config,
                self.custom_conf,
                self.get_controller_conf(controller),
                DefaultConfig
                ]
            if a])
        return wrap

    def get_controller_conf(self, controller):
        return controller.config if hasattr(controller, 'config') else None


def q_comp(q, name):
    if type(q) == bool:
        if q:
            return lambda a:{name:a}
        else:
            def hello(a):
                if a:
                    raise TypeError
                else:
                    return {}
            return hello
    elif issubclass(type(q), (list,tuple)):
        return lambda a: {arg:a.get(arg) for arg in q}
    else:
        raise TypeError


class ControlFunction:
    def __init__(self, function, prefix, regex, get, post):
        self.function = function
        self.prefix = prefix
        self.regex = re.compile(regex) if isinstance(regex, str) else regex
        self.get = q_comp(get, 'get')
        self.post = q_comp(post, 'post')
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance:
            return self.function(self.instance, *args, **kwargs)
        return self.function(*args, **kwargs)

    def __repr__(self):
        if self.instance:
            return '<ControlMethod for prefix \'' + self.prefix + '\' with function ' + self.function + ' and instance ' + repr(self.instance) + '>'
        return '<ControlFunction for prefix \'' + self.prefix + '\' with function ' + repr(self.function) + '>'


def controller_function(prefix, regex:str=None, *, get=True, post=True):
    def wrap(func):
        controller_mapper.add_controller(prefix, ControlFunction(func, prefix, regex, get, post))
        return func
    return wrap


def controller_class(class_):
    c_funcs = list(filter(lambda a: isinstance(a, ControlFunction), class_.__dict__.values()))
    if c_funcs:
        instance = class_()
        controller_mapper._controller_classes.append(instance)
        for item in c_funcs:
            item.instance = instance
            controller_mapper.add_controller(item.prefix, item)
    return class_


def controller_method(prefix, regex:str=None, *, get=True, post=True):
    def wrap(func):
        wrapped = ControlFunction(func, prefix, regex, get, post)
        return wrapped
    return wrap


class url_args:
    """
    Function decorator for controller Methods. Parses the Input (url) without prefix according to the regex.
    Unpacks groups into function call arguments.

    get and post can be lists of arguments which will be passed to the function as keyword arguments or booleans
    if get/post are true the entire query is passed to the function as keyword argument 'get' or 'post'
    if get/post are false no queries will passed

    if strict is true, only specified values will be accepted,
    and the existence of additional arguments will cause an error.

    :param regex: regex pattern or string
    :param get: list/tuple (subclasses) or boolean
    :param post: list/tuple (subclasses) or boolean
    :param strict: boolean
    :return:
    """
    def __init__(self, regex, *, get=False, post=False, strict:bool=False):
        self.get = self.q_comp(get, 'get')
        self.post = self.q_comp(post, 'post')
        self.regex = isinstance(regex, str) if re.compile(regex) else regex
        self.strict = strict

    def q_comp(self, q, name):
        if type(q) == bool:
            if q:
                return lambda a:{name:a}
            elif self.strict:
                return lambda a: bool(a) if False else {}
            else:
                return lambda a: {}
        elif issubclass(type(q), (list,tuple)):
            if self.strict:
                def f(a:list, b:dict):
                    d = b.copy()
                    for item in a:
                        if item not in d:
                            raise TypeError
                    return d
                return lambda a: len(q) == len(a.keys()) if f(q, a) else False
            return lambda a: {arg:a.get(arg) for arg in q}
        else:
            raise TypeError

    def __call__(self, func):
        def _generic(model, url, client):
            kwargs = dict(client=client)
            for result in [self.get(url.get_query), self.post(url.post)]:
                if result is False:
                    raise TypeError
                else:
                    kwargs.update(result)
            # return re.match(regex, str(url.path)).groups(), kwargs
            return func(*(model, ) + re.match(self.regex, url.path.prt_to_str(1)).groups(), **kwargs)
        return _generic