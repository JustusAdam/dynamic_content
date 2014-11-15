from urllib.error import HTTPError

from dynct.errors.exceptions import OverwriteProhibitedError


__author__ = 'justusadam'


_register_controllers = True


class Controller(dict):
    pass


class ControllerMapper(dict):

    def register_modules(self):
        from dynct.core import Modules
        for l in Modules.get_handlers_by_class(Controller).values():
            for c in l:
                self.register_controller(c)

    def register_controller(self, controller_class):
        print(controller_class)
        instance = controller_class()
        if _register_controllers:
            if not hasattr(self, '_controller_classes'):
                self._controller_classes = []
            if not controller_class in self._controller_classes:
                self._controller_classes.append(controller_class)
            if not hasattr(self, '_controller_instances'):
                self._controller_instances = []
            self._controller_instances.append(instance)

        for key, value in instance.items():
            self[key] = value

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