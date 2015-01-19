import functools
from http import cookies
from . import config
from dyc.includes import settings


__author__ = 'Justus Adam'
__version__ = '0.1'


class Context(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__final = False
        self.decorator_attributes = set()
        self.headers = dict()
        self.cookies = cookies.SimpleCookie()
        self.config = config.Config()
        self.theme = settings.DEFAULT_THEME
        self.client = None

    def __setitem__(self, key, value):
        if self.__final:
            return
        dict.__setitem__(self, key, value)

    def assign_key_safe(self, key, value):
        if key in self and self[key]:
            print('key ' + key + ' already exists in model')
        else:
            self.__setitem__(key, value)

    def finalize(self):
        self.__final = True


def apply_to_context(apply_before=True, return_from_decorator=False, with_return=False):
    """
    Apply the outer decorated function to the inner decorated functions first argument
    :param apply_before:
    :param return_from_decorator:
    :param with_return:
    :return:
    """
    def wrapper(func):
        def inner_wrapper(inner_func):
            functools.wraps(inner_func)(func)

            def inner_call(*args, **kwargs):
                context = args[0] if isinstance(args[0], Context) else args[1]
                if apply_before:
                    res_dec = func(context)
                    res = inner_func(*args, **kwargs)

                else:
                    res = inner_func(*args, **kwargs)
                    if with_return:
                        res_dec = func(context, res)
                    else:
                        res_dec = func(context)

                if return_from_decorator:
                    return res_dec
                else:
                    return res

            return inner_call
        return inner_wrapper
    return wrapper