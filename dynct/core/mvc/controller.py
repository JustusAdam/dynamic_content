from collections import ChainMap
import re
from dynct.util.misc_decorators import deprecated


__author__ = 'justusadam'


_register_controllers = True


def authorize(permission):
    pass


@deprecated
class Controller(dict):
    pass


class ControllerMapper(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._controller_classes = []

    def register_modules(self):
        from dynct.core import Modules
        self.modules = Modules


    def __getitem__(self, item):
        return self.setdefault(item, list())

    def add_controller(self, prefix, function):
        self.setdefault(prefix, list()).append(function)


    def __call__(self, model, url):
        l = str(url.path).split('/', 2)
        if not l[0] == '' or len(l) < 2: raise AttributeError
        prefix = l[1]
        path = l[2] if len(l) > 2 else ''
        elements = self[prefix]
        for element in elements:
            if element.regex:
                m = re.fullmatch(element.regex, path)
                if not m:
                    continue
                else:
                    args = m.groups()
            else:
                args = (url, )
            try:
                get, post = element.get(url.get_query), element.post(url.post)
                result = element(model, *args, **dict(ChainMap(get, post)))
                if not result:
                    continue
                else:
                    return result
            except PermissionError as e:
                print(e)
                continue
        return 'error'



controller_mapper = ControllerMapper()