import unittest
from dyc import core
from dyc.core import mvc
from dyc.core.mvc.context import Context
from dyc import dchttp

__author__ = 'Justus Adam'


class TestDecorator(unittest.TestCase):

    def test_discovery(self):

        prefix1 = 'hello/{str}'
        testpath = 'somepath35'
        model = Context()

        @mvc.controller_function(prefix1, method=dchttp.RequestMethods.GET, query=True)
        def handle(model, arg, get):
            return model, arg, get

        r = dchttp.Request('localhost', 8080, '/hello/' + testpath, 'get', {}, None, False)
        handler, args, kwargs = core.get_component('PathMap').resolve(r)
        result_model, result_arg, result_get = handler(model, *args, **kwargs)
        self.assertEqual(model, result_model)
        self.assertEqual(testpath, result_arg)
        self.assertEqual({}, result_get)