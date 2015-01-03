import functools

__author__ = 'justusadam'


def ensure_loaded(loadable):
    @functools.wraps(loadable)
    def wrap(instance, *args, **kwargs):
        if not instance.loaded:
            instance.load()
            instance.loaded = True
        return loadable(instance, *args, **kwargs)

    return wrap


class Loadable(object):
    def __init__(self):
        self.loaded = False

    def load(self):
        raise NotImplementedError


class LoadableDict(dict, Loadable):
    def __init__(self, iterable, **kwargs):
        super().__init__(iterable, **kwargs)
        Loadable.__init__(self)

    @ensure_loaded
    def __getitem__(self, item):
        return super().__getitem__(item)

    @ensure_loaded
    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

    @ensure_loaded
    def __repr__(self):
        return super().__repr__()

    @ensure_loaded
    def __str__(self):
        return super().__str__()