__author__ = 'justusadam'


def proxy_method(lazy_obj):
    def wrapper(*args, **kwargs):
        if not lazy_obj._wrapped:
            lazy_obj._setup()
        return lazy_obj(*args, **kwargs)
    return wrapper


class lazy(object):
    _wrapped = None

    def _setup(self):
        print('executing _setup')

    def __init__(self, _class):
        self.wclass = _class

