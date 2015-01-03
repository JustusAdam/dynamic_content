import inspect
from functools import wraps
from dyc.includes import settings

__author__ = 'justusadam'


def typesafe(func):
    if settings.RUNLEVEL == settings.RunLevel.production: return func
    spec = inspect.getfullargspec(func)
    types = spec.annotations
    def_args = spec.args

    def checkargs(argval):
        for arg, value in argval:
            if arg in types:
                if not isinstance(value, types[arg]):
                    raise TypeError('Typechecking: expected type ' + str(types[arg]) + ' but found ' + str(type(value)))

    @wraps(func)
    def wrap(*args, **kwargs):
        real_args = [a for a in def_args if a not in kwargs]

        checkargs(zip(real_args, args))
        checkargs(kwargs.items())
        res = func(*args, **kwargs)
        checkargs([['return', res]])
        return res

    return wrap