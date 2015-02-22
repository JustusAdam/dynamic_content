import inspect
import sys

from functools import wraps

__author__ = 'Justus Adam'


def typesafe(func):
    """
    Perform typechecking on set type annotations of functions

    :param func: function to wrap
    :return: func(*args, *kwargs)
    """
    if getattr(sys.flags, 'optimize', 0) == 1:
        return func
    spec = inspect.getfullargspec(func)
    types = spec.annotations
    def_args = spec.args

    def checkargs(argval):
        """
        Check each argument for correct type

        :param argval: iterable of arguments + names
        :return: None
        """
        for arg, value in argval:
            if arg in types:
                if not isinstance(value, types[arg]):
                    raise TypeError('Typechecking: expected type ' + str(types[arg]) + ' but found ' + str(type(value)))

    @wraps(func)
    def wrap(*args, **kwargs):
        """
        Function wrapper


        :param args: function args
        :param kwargs: function kwargs
        :return: function return
        """
        real_args = (a for a in def_args if a not in kwargs)

        checkargs(zip(real_args, args))
        checkargs(kwargs.items())
        res = func(*args, **kwargs)
        checkargs((('return', res),))
        return res

    return wrap