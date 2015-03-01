"""
Implementation of classes and helper functions
delaying intantiation or initialization
"""

import functools

__author__ = 'Justus Adam'


def ensure_loaded(loadable):
    """
    Decorator for methods that require the object instance to be loaded

    :param loadable: the decorated method
    :return: wrapper
    """
    @functools.wraps(loadable)
    def wrap(instance, *args, **kwargs):
        """
        lazy.ensure_loaded inner wrapping function
        that ensures the instance is loaded

        :param instance: functions 'self'
        :param args: wrapped method call args
        :param kwargs: wrapped method call kwargs
        :return: loadable(instance, *args, **kwargs)
        """
        if not instance.loaded:
            instance.load()
            instance.loaded = True
        return loadable(instance, *args, **kwargs)

    return wrap


class Loadable(object):
    """
    An object whose initilizing statements are put into load()
    to postpone their execution
    """
    __slots__ = 'loaded',

    def __init__(self):
        self.loaded = False

    def load(self):
        """
        Meat of the object. this is where the actual loading work goes.
        """
        raise NotImplementedError

#
# class LoadableDict(dict, Loadable):
#     """
#     A dictionary version of the loadable class
#     """
#     __slots__ = ()
#
#     def __init__(self, iterable, **kwargs):
#         super().__init__(iterable, **kwargs)
#         Loadable.__init__(self)
#
#     @ensure_loaded
#     def __getitem__(self, item):
#         return super().__getitem__(item)
#
#     @ensure_loaded
#     def __setitem__(self, key, value):
#         return super().__setitem__(key, value)
#
#     @ensure_loaded
#     def __repr__(self):
#         return super().__repr__()
# 
#     @ensure_loaded
#     def __str__(self):
#         return super().__str__()
