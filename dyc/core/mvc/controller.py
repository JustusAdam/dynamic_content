from dyc import dchttp
from dyc.util import decorators
from .. import _component


__author__ = 'Justus Adam'
__version__ = '0.1'


_register_controllers = True


@decorators.deprecated
class Controller(dict):
    pass


@decorators.deprecated
@_component.Component('ControllerMapping')
class ControllerMapper(object):
    def __init__(self):
        super().__init__()
        self._controller_classes = []
        self.register_modules()
        self.any_method = {}

    def register_modules(self):
        self.modules = _component.get_component('Modules')


    def __call__(self, model, url):
        prefix, *path = str(url.path).split('/', 2)
        if not prefix == '': raise AttributeError
        path = path[0]

        query = (
            url.get_query
            if url.method == dchttp.RequestMethods.POST
            else url.post
            )


        def proc_one(element):
            pass
