import unittest
from framework import route, http
from framework.machinery import component
from framework.util import structures

__author__ = 'Justus Adam'


class TestDecorator(unittest.TestCase):

    def test_discovery(self):

        prefix1 = 'hello/{str}'
        testpath = 'somepath35'
        r = http.Request('localhost', 8080, '/hello/' + testpath, 'get', {}, None, False)
        model = structures.DynamicContent(
            request=r,
            context={},
            config={},
            handler_options={}
        )

        @route.controller_function(prefix1, method=http.RequestMethods.GET, query=True)
        def handle(model, arg, get):
            return model, arg, get

        handler, args, kwargs = component.get_component('PathMap').get().resolve(r)
        result_model, result_arg, result_get = handler(model, *args, **kwargs)
        self.assertEqual(model, result_model)
        self.assertEqual(testpath, result_arg)
        self.assertEqual({}, result_get)
