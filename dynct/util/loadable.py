import functools

__author__ = 'justusadam'



def ensure_loaded(loadable):
    @functools.wraps(loadable)
    def wrap(self, *args, **kwargs):
        if not self.loaded:
            self.load()
            self.loaded = True
        return loadable(self, *args, **kwargs)
    return wrap


class Loadable(object):
    def __init__(self):
        self.loaded = False

    def load(self):
        pass