import functools
import os
import inspect

from dyc.includes import log, settings


__author__ = 'Justus Adam'


def deprecated(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if settings.LOGGING_LEVEL == settings.LoggingLevel.THROW_ALL:
            raise DeprecationWarning
        if settings.LOGGING_LEVEL == settings.LoggingLevel.LOG_WARNINGS:
            log.write_warning(function=repr(func), message='using deprecated function')
        return func(*args, **kwargs)

    return wrap


Deprecated = deprecated


def filter_args(types, args, kwargs):
    all_args = list(args) + list(kwargs.values())
    for t in types:
        yield filter_([arg for arg in all_args if isinstance(arg, t)], t)


def filter_(list_, type_):
    if len(list_) == 1:
        return list_[0]
    perfect = [a for a in list_ if type(a) == type_]
    if perfect:
        return perfect[0]
    else:
        return list_[0]


class apply_to_type:
    """
    Decorator for decorators.
    Takes types as arguments (must be unique) and decorates or wraps a decorator or wrapper of a function.

    When called will make a list of arguments from args and kwargs
     corresponding to the specified types (and in the same order).
     It will later pass this list to the decorator.

    :param apply_before: if true the decorator is called first, then the function (all return values are cashed),
     if false the function is called first then the decorator (all return values are cashed)

    :param return_from_decorator: if true the cashed result from calling the decorator is returned, if false the
     cashed result from calling the function is returned

    :param apply_in_decorator: if true the decorator will be called with a callback (instead of with the custom list) first
     that, if called (with no parameters) executes the function and returns the result
     and called again with the custom argument list.
     If this option is true this decorator will never call the function and the return value
     will be the return value from the wrapped decorator

    """

    def __init__(self, *types, apply_before=True, return_from_decorator=False, apply_in_decorator=False,
                 overwrite_input=False):
        assert len(set(types)) == len(types)
        self.types = types
        self.apply_before = apply_before
        self.return_ = return_from_decorator
        self.apply_in = apply_in_decorator
        self.overwrite = overwrite_input

    def __call__(self, decorator):
        self.decorator = decorator

        def wrap(func):
            @functools.wraps(func)
            def wrap_inner(*args, **kwargs):

                def applyd():
                    l = filter_args(self.types, args, kwargs)
                    if self.apply_in:
                        return self.decorator(applyf)(*l)
                    return self.decorator(*l)

                def applyf(*fargs, **fkwargs):
                    try:
                        if self.overwrite:
                            return func(*fargs, **fkwargs)
                        else:
                            return func(*args, **kwargs)
                    except TypeError as e:
                        print(func)
                        raise e

                if self.apply_in:
                    return applyd()

                if self.apply_before:
                    resd = applyd()
                    resf = applyf()
                else:
                    resf = applyf()
                    resd = applyd()

                return self.return_ if resd else resf

            return wrap_inner

        return wrap

    def __repr__(self):
        return '<function ' + repr(self.decorator) + ' wrapped with apply_to_type>'


class requiredir:
    def __init__(self, directory):
        self.directory = directory
        self.curr_dir = os.getcwd()

    def __call__(self, f):
        self.curr_dir = os.getcwd()

        def wrapper(*args, **kwargs):
            os.chdir(self.directory)
            f(*args, **kwargs)
            os.chdir(self.curr_dir)

        return wrapper


def implicit(arg):
    def w(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(arg, *args, **kwargs)

        return wrapped

    return w


def for_method_and_func(_generic):
    def wrap(func):
        def _method(self, *args, **kwargs):
            args, kwargs = _generic(*args, **kwargs)
            return func(self, *args, **kwargs)

        def _function(*args, **kwargs):
            args, kwargs = _generic(*args, **kwargs)
            return func(*args, **kwargs)

        if inspect.ismethod(func):
            return _method
        elif inspect.isfunction(func):
            return _function
        else:
            raise TypeError

    return wrap


def multicache(func):
    _cache = {}

    @functools.wraps(func)
    def wrap(*args):
        return _cache.setdefault(args, func(*args))

    return wrap


class singlecache:
    def __init__(self, func):
        self._cache = None
        self.func = func

    def __call__(self, *args):
        if not hasattr(self, '_args') or not args == self._args:
            self._args = args
            self._cache = self.func(*args)
        return self._cache


def typecast(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        pass

    return wrap


def transformarg(transformer, name, index):
    def wrap(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if name in kwargs:
                res = dict(**kwargs)
                res[name] = transformer(kwargs[name])
                return func(*args, **res)
            else:
                item = transformer(args[index])
                return func(*args[:index] + (item,) + args[index + 1:], **kwargs)

        return inner

    return wrap


transform_with = lambda transformer: functools.partial(transformarg, transformer)


def catch(exception, return_value=None, print_error=True, log_error=True):
    def wrap(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                if print_error:
                    print(e)
                if log_error:
                    log.write_error(function=repr(func), message=repr(e))
                return return_value
        return _inner
    return wrap


def vardump():
    print(locals())
    print(globals())