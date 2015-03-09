"""
This module defines decorators to use for registering and interacting
with the dynamic_content model-view-controller implementation

Important interactions are:

 Registering a new view/controller function:

  Annotate the function with @controller_function(*args) or
   @rest_controller_function(*args)

  ... more doc to follow

  **options allow you to specify further flags and options that
  might be interesting to other parts of the framework,
  mostly used by view middleware

  known options are:

   anti_csrf (boolean, default=True):  when set to false no anti-csrf token
    checking is performed on requests to the path handled by this controller
   require_ssl (boolean, default=False): when set to true a middleware will
    redirect any http request to this controller to the appropriate https url
    provided the server currently has https enabled


It is recommended to not directly use ControllerFunction and
RestControllerFunction.
"""

import functools

from ..machinery import component, scanner, linker
from framework import http
from framework.mvc import context
from framework.util import rest
import inspect


__author__ = 'Justus Adam'
__version__ = '0.2'


@component.inject('PathMap')
def get_cm(cm):
    return cm


def _to_set(my_input, allowed_vals=str):
    if isinstance(my_input, frozenset):
        return my_input
    elif isinstance(my_input, set):
        return frozenset(my_input)
    if isinstance(my_input, (list, tuple)):
        for i in my_input:
            if not isinstance(i, allowed_vals):
                raise TypeError(
                    'Expected type {} got {}'.format(
                        allowed_vals, type(my_input))
                        )
        return frozenset(my_input)
    elif isinstance(my_input, allowed_vals):
        return frozenset({my_input})
    else:
        raise TypeError('Expected type {} or {} got {}'.format(
            (list, tuple, set, frozenset), allowed_vals, type(my_input)
            ))


class ControlFunction:
    """
    Object representing a function/method that handles one or more paths
    """
    __slots__ = (
        'function', 'wrapping', 'value',
        'method', 'query', 'headers',
        'instance', 'typeargs', 'options'
    )

    def __init__(self, function, value, method, query, headers, options=None):
        if isinstance(function, ControlFunction):
            self.function = function.function
            self.wrapping = function.wrapping
        else:
            self.wrapping = []
            self.function = function
        self.wrapping.append(self)
        self.value = _to_set(value)
        self.method = _to_set(method, str)
        self.query = query if isinstance(query, (dict, bool)) else _to_set(query)
        self.headers = frozenset() if headers is None else _to_set(headers)
        self.instance = None
        self.typeargs = []
        self.options = options if options is not None else {}

    def __call__(self, *args, **kwargs):
        if self.instance:
            return self.function(self.instance, *args, **kwargs)
        return self.function(*args, **kwargs)

    def __repr__(self):
        return '<ControlFunction for path(s) \'{}\' with {}>'.format(
            self.value, self.function
            )


class RestControlFunction(ControlFunction):
    """
    Control function with json return
    """
    __slots__ = ()

    def __call__(self, model, *args, **kwargs):
        model.json_return = super().__call__(*args, **kwargs)
        model.decorator_attributes |= {'no-view', 'json-format', 'string-return'}
        return model


class ControllerClass:
    __slots__ = 'inner',

    def __init__(self, class_):
        self.inner = class_

    def get(self):
        return self.inner


def _controller_function(
    class_,
    value,
    *,
    method=http.RequestMethods.GET,
    headers=frozenset(),
    query=False,
    **options
    ):
    def wrap(func):
        h = (http.headers.Header.auto_construct(headers)
             if headers is not None
             else None)
        h = set(h) if inspect.isgenerator(h) else {h}
        wrapped = class_(func, value, method, query, h, options)
        for val in wrapped.value:
            get_cm().add_path(val, wrapped)
        return wrapped
    return wrap


def _controller_method(
        class_,
        value,
        *,
        method=http.RequestMethods.GET,
        headers=frozenset(),
        query=False,
        **options
    ):
    def wrap(func):
        h = http.headers.Header.auto_construct(headers) if headers is not None else None
        h = frozenset(h) if inspect.isgenerator(h) else frozenset({h})
        wrapped = class_(func, value, method, query, h, options)
        return wrapped
    return wrap


controller_function = functools.partial(_controller_function, ControlFunction)


def controller_class(class_):
    c_funcs = tuple(filter(
        lambda a: isinstance(a, ControlFunction),
        class_.__dict__.values()
        ))
    if c_funcs:
        instance = class_()
        get_cm()._controller_classes.append(instance)
        for item in c_funcs:
            for wrapped in item.wrapping:
                wrapped.instance = instance
                for i in wrapped.value:
                    get_cm().add_path(i, wrapped)
    return ControllerClass(class_)


@scanner.MatchingTypeHook.make(ControlFunction)
class RouteLink(linker.SimpleLink):
    __slots__ = ()

    def unlink_action(self):
        raise NotImplementedError

    def link_action(self):
        for i in self.variable.value:
            get_cm().add_path(i, self.variable)


@scanner.MatchingTypeHook.make(ControllerClass)
def class_registerer(module, cc):
    c_funcs = tuple(filter(
        lambda a: isinstance(a, ControlFunction),
        cc.__dict__.values()
        ))
    if c_funcs:
        instance = cc()
        get_cm()._controller_classes.append(instance)
        for item in c_funcs:
            for wrapped in item.wrapping:
                wrapped.instance = instance
                yield RouteLink(module, wrapped)


controller_method = functools.partial(_controller_method, ControlFunction)

rest_controller_function = functools.partial(_controller_function, RestControlFunction)

rest_controller_method = functools.partial(_controller_method, RestControlFunction)


@context.apply_to_context(return_from_decorator=True, with_return=True)
def json_return(context, res):
    return rest.json_response(res, context)