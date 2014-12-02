import unittest
from dynct.core.mvc import controller_mapper
from dynct.core.mvc.decorator import controller_function
from dynct.core.mvc.model import Model
from dynct.util.url import Url

__author__ = 'justusadam'


class TestDecorator(unittest.TestCase):

    def test_discovery(self):

        prefix1, regex1, get1, post1 = 'hello', '(.*)', True, False
        testpath = '/somepath35'
        url1 = Url('/hello' + testpath)
        model = Model()
        @controller_function(prefix1, regex1, get=get1, post=post1)
        def handle(model, arg, get):
            return model, arg, get

        result_model, result_arg, result_get = controller_mapper(model, url1)
        self.assertEqual(result_model, model)
        self.assertEqual(result_arg, testpath)
        self.assertEqual(result_get, {})