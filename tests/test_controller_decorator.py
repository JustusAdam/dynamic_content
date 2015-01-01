import unittest
from dyc import core
from dyc.core import mvc
from dyc.core.mvc.model import Model
from dyc import dchttp
from dyc.util.url import Url

__author__ = 'justusadam'


class TestDecorator(unittest.TestCase):

    def test_discovery(self):

        prefix1 = 'hello/{str}'
        testpath = 'somepath35'
        url1 = Url('/hello/' + testpath)
        url1.method = 'get'
        model = Model()

        @mvc.controller_function(prefix1, method=dchttp.RequestMethods.GET, query=True)
        def handle(model, arg, get):
            return model, arg, get

        result_model, result_arg, result_get = core.get_component('PathMap')(model, url1)
        self.assertEqual(model, result_model)
        self.assertEqual(testpath, result_arg)
        self.assertEqual({}, result_get)