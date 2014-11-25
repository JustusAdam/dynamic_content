import os
import inspect

from dynct.errors import InvalidInputError


__author__ = 'justusadam'


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
    def __init__(self, *types, apply_before=True, return_from_decorator=False, apply_in_decorator=False):
        assert len(set(types)) == len(types)
        self.types = types
        self.apply_before = apply_before
        self.return_ = return_from_decorator
        self.apply_in = apply_in_decorator

    def __call__(self, decorator):
        self.decorator = decorator

        def wrap(func):
            def wrap_inner(*args, **kwargs):
                def filter_(list_, type_):
                    if len(list_) == 1:
                        return list_[0]
                    perfect = [a for a in list_ if type(a) == type_]
                    if perfect:
                        return perfect[0]
                    else:
                        return list_[0]

                def applyd():
                    all_args = list(args) + list(kwargs.values())
                    l = [
                        filter_([arg for arg in all_args if isinstance(arg, t)], t) for t in self.types
                    ]
                    if self.apply_in:
                        return self.decorator(applyf)(*l)
                    return self.decorator(*l)

                def applyf():
                    try:
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
            raise InvalidInputError
    return wrap


def multicache(func):
    _cache = {}
    def wrap(*args):
        return _cache.setdefault(args, func(*args))


class singlecache:
    def __init__(self, func):
        self._cache = None
        self.func = func

    def __call__(self, *args):
        if not hasattr(self, '_args') or not args == self._args:
            self._args = args
            self._cache = self.func(args)
        return self._cache