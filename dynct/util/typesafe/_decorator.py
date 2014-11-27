import inspect

__author__ = 'justusadam'


def typesafe(func):
    spec = inspect.getfullargspec(func)
    types = spec.annotations
    def_args = spec.args
    def checkargs(argval):
        for arg, value in argval:
            if arg in types:
                assert isinstance(value, types[arg])
    def wrap(*args, **kwargs):
        real_args = [a for a in def_args if a not in kwargs]

        checkargs(zip(real_args, args))
        checkargs(kwargs.items())
        res = func(*args, **kwargs)
        checkargs([['return', res]])
        return res
    return wrap