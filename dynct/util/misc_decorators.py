import os
import inspect
from dynct.errors import InvalidInputError

__author__ = 'justusadam'


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