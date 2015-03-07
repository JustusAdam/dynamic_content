import functools
import inspect
import logging

from framework.includes import get_settings
from framework.util import structures


__author__ = 'Justus Adam'


def deprecated(func):
    """
    Mark a function as not to be used anymore
    This will create log messages every time the function gets called

    :param func: wrapped function
    :return: wrapper
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        logging.getLogger(func.__module__).warning(
            'using deprecated function {}'.format(func)
        )
        return func(*args, **kwargs)

    return wrap


# for convenience of those who like to roll with caps
Deprecated = deprecated


def filter_args(types, args, kwargs):
    """
    Filter all arguments (and kwargs) for those which match provided types
    """

    all_args = args + tuple(kwargs.values())

    # iterate over all types we need
    for type_ in types:

        # try to potentially find a type matching exactly
        perfect_type_match = filter(lambda a: type(a) == type_, all_args)

        try:
            # try to yield the first element from the filter
            yield perfect_type_match.__next__()
        except StopIteration:
            # the perfect_match was empty
            try:
                # try looking for subclasses
                filtered = filter(
                    lambda a: isinstance(a,type_), all_args
                )
                # try yielding one element
                yield filtered.__next__()
            except StopIteration:
                # in none of that succeeded we throw an exception
                raise TypeError('no argument with type {} found'.format(type_))


class apply_to_type:
    """
    Decorator for decorators.
    Takes types as arguments (must be unique)
    and decorates or wraps a decorator or wrapper of a function.

    If the wrapped function gets called with (a) subtype of two of the
    types you specified it is ambiguous to the function how these
    would be matched, and as such the behaviour in this casse
    is undefined for performance reasons

    When called will make a list of arguments from args and kwargs
     corresponding to the specified types (and in the same order).
     It will later pass this list to the decorator.

    :param apply_before: if true the decorator is called first,
                         then the function (all return values are cashed),
                         if false the function is called first,
                         then the decorator (all return values are cashed)

    :param return_from_decorator: if true the cashed result from calling
                                  the decorator is returned, if false the
                                  cashed result from calling
                                  the function is returned

    :param apply_in_decorator: if true the decorator will be called with
                               a callback (instead of with the custom list)
                               first that, if called (with no parameters)
                               executes the function and returns the result
                               and called again with the custom argument list.
                               If this option is true this decorator will never
                               call the function and the return value
                               will be the return value from the wrapped
                               decorator

    """
    __slots__ = (
        'types',
        'apply_before',
        'return_',
        'apply_in',
        'overwrite',
        'decorator'
    )

    def __init__(
            self,
            *types,
            apply_before=True,
            return_from_decorator=False,
            apply_in_decorator=False,
            overwrite_input=False
    ):
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
                        logging.getLogger(__name__).error(func)
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


@deprecated
def multicache(func):
    _cache = {}

    @functools.wraps(func)
    def wrap(*args):
        return _cache.setdefault(args, func(*args))

    return wrap


class singlecache:
    """save only one call to func"""
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


def catch(exception, return_value=None, log_error=True):
    def wrap(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                if log_error:
                    logging.getLogger(__name__).error(
                        '{} errored with exception: {}'.format(func, e)
                    )
                return return_value
        return _inner
    return wrap


def vardump():
    logging.getLogger(__name__).error(locals())
    logging.getLogger(__name__).error(globals())
