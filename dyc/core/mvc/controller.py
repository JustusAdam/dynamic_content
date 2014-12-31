import re
from urllib import error
from dyc import dchttp
from dyc.util import decorators
from .. import _component


__author__ = 'justusadam'

_register_controllers = True


@decorators.deprecated
class Controller(dict):
    pass


@_component.Component('ControllerMapping')
class ControllerMapper(object):
    def __init__(self):
        super().__init__()
        self._controller_classes = []
        self.register_modules()
        self.any_method = {}

    def register_modules(self):
        self.modules = _component.get_component('Modules')

    # def sort(self):
    #     """
    #     Sorts all controller functions such that:
    #       1. functions with a specified regex will be preferred over those with None (or '')
    #       2. functions with longer regex will be preferred over shorter ones
    #       3. functions that accept no query or only specific keys will be preferred over
    #        those that accept any.
    #
    #     This should in theory ensure, that more specific 'paths' are preferred over generic ones.
    #     """
    #     for ditem in self.values():
    #         for item in ditem.values():
    #             # TODO check if this works correctly
    #             item.sort(key=lambda a: int(bool(a.method)))
    #             item.sort(key=lambda a: len(a.orig_pattern) if a.orig_pattern else 0, reverse=True)
    #
    # def add_controller(self, prefix, function):
    #     if function.method:
    #         if isinstance(function.method, str):
    #             self.setdefault(function.method.lower(), dict()).setdefault(prefix, list()).append(function)
    #         elif isinstance(function.method, (list, tuple, set)):
    #             for method in function.method:
    #                 self.setdefault(method.lower(), dict()).setdefault(prefix, list()).append(function)
    #     else:
    #         self.any_method.setdefault(prefix, list()).append(function)


    def __call__(self, model, url):
        prefix, *path = str(url.path).split('/', 2)
        if not prefix == '': raise AttributeError
        path = path[0]

        query = url.get_query if url.method == dchttp.RequestMethods.POST else url.post


        def proc_one(element):
            if element.query is True:
                return element(model, (query, ))
            elif query:
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

        try:
            e = self[url.method.lower()](path)

            res = proc_one(e)

            if res:
                return res
            else:
                res = proc_one(self.any_method[prefix])
                if res:
                    return res
        except KeyError as err:
            print(err)
            raise error.HTTPError(str(url), 404, 'no page matching query found', None, None)

        return 'error'