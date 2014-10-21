__author__ = 'justusadam'


class Request:

    type = None

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs