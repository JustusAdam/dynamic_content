from errors.exceptions import OverwriteProhibitedError

__author__ = 'justusadam'


class Request(object):
    type = None
    _target = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @property
    def target(self):
        if not self._target:
            return self.args[0]
        return self._target

    @target.setter
    def target(self, value):
        self._target = value