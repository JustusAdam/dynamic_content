import re
from dynct.util import decorators
from .. import _component


__author__ = 'justusadam'

_register_controllers = True


@decorators.deprecated
class Controller(dict):
    pass


@_component.Component('ControllerMapping')
class ControllerMapper(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._controller_classes = []
        self.register_modules()
        self.any_method = {}

    def register_modules(self):
        self.modules = _component.get_component('Modules')

    def sort(self):
        """
        Sorts all controller functions such that:
          1. functions with a specified regex will be preferred over those with None (or '')
          2. functions with longer regex will be preferred over shorter ones
          3. functions that accept no query or only specific keys will be preferred over
           those that accept any.

        This should in theory ensure, that more specific 'paths' are preferred over generic ones.
        """
        for ditem in self.values():
            for item in ditem.values():
                # TODO check if this works correctly
                item.sort(key=lambda a: int(bool(a.method)))
                item.sort(key=lambda a: len(a.orig_pattern) if a.orig_pattern else 0, reverse=True)

    def add_controller(self, prefix, function):
        if function.method:
            if isinstance(function.method, str):
                self.setdefault(function.method.lower(), dict()).setdefault(prefix, list()).append(function)
            elif isinstance(function.method, (list, tuple, set)):
                for method in function.method:
                    self.setdefault(method.lower(), dict()).setdefault(prefix, list()).append(function)
        else:
            self.any_method.setdefault(prefix, list()).append(function)


    def __call__(self, model, url):
        l = str(url.path).split('/', 2)
        if not l[0] == '' or len(l) < 2: raise AttributeError
        prefix = l[1]
        path = '/' + l[2] if len(l) > 2 else ''

        query = url.get_query if url.method == 'get' else url.post

        def proc_one(element):
            if element.regex:
                m = re.fullmatch(element.regex, path)
                if not m:
                    return
                else:
                    args = m.groups()
            else:
                args = (url, )

            if query:
                if isinstance(element.query, str):
                    return element(model, *args, **{element.query: query.get(element.query, None)})
                elif isinstance(element.query, (list, tuple, set)):
                    return element(model, *args, **{a : query.get(a, None) for a in element.query})
                elif isinstance(element.query, dict):
                    return element(model, *args, **{b : query.get(a, None) for a, b in element.query.items()})
            else:
                if element.query is False:
                    return element(model, *args)
                else:
                    return

        def proc_all(elements):
            for element in elements:
                res = proc_one(element)
                if res:
                    return res

        e = self[url.method.lower()][prefix]

        res = proc_all(e)

        if res:
            return res
        else:
            res = proc_all(self.any_method[prefix])
            if res:
                return res

        return 'error'