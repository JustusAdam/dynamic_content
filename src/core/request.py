from errors.exceptions import OverwriteProhibitedError

__author__ = 'justusadam'


class Request(object):

    type = None

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise OverwriteProhibitedError
        else:
            super().__setattr__(key, value)