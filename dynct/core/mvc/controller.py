from collections import ChainMap


__author__ = 'justusadam'


_register_controllers = True


def authorize(permission):
    pass


class Controller(dict):
    pass

#
# class RegexURLMapper(Controller):
#     pass



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

    def __getitem__(self, item):
        return self.setdefault(item, list())


    def __call__(self, model, url):
        start, prefix, path = str(url.path).split('/', 2)
        if start != '':
            raise TypeError
        elements = self[prefix]
        for element in elements:
            m = element.regex.fullmatch(path)
            if not m:
                continue
            try:
                get, post = element.get(url.get_query), element.post(url.post)
                result = element.function(model, *m.groups(), **dict(ChainMap(get, post)))
                if not result:
                    continue
                else:
                    return result
            except TypeError:
                continue



controller_mapper = ControllerMapper()