from urllib.error import HTTPError

from dynct.errors.exceptions import OverwriteProhibitedError


__author__ = 'justusadam'


class Controller(dict):
    pass


class ControllerMapper(dict):
    controllers = set()

    def register_modules(self):
        from dynct.core import Modules
        for c in Modules.get_handlers_by_class(Controller):
            self.register_controller(c)

    def register_controller(self, controller):
        for item in controller:
            self.__setitem__(item, controller[item])

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        if key in self:
            raise OverwriteProhibitedError
        super().__setitem__(key, value)

    def __call__(self, url):
        if url.path[0] in self:
            return self[url.path[0]]
        else:
            raise HTTPError(str(url), 404, None, None, None)