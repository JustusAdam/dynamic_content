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
        pass