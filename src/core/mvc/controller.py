import inspect
from errors.exceptions import OverwriteProhibitedError

__author__ = 'justusadam'


class Controller(dict):
    pass


class ControllerMapper(dict):
    controllers = set()

    def register_module(self, module):
        for attr in module.__dict__.values():
            if inspect.isclass(attr):
                if issubclass(attr, Controller):
                    c = attr()
                    self.controllers.add(c)
                    self.register_controller(c)

    def register_controller(self, controller):
        for item in controller:
            self.__setitem__(item, controller[item])

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, Controller)
        if key in self:
            raise OverwriteProhibitedError
        super().__setitem__(key, value)

    def __call__(self, url):
        return self[url.path[0]]