import unittest

from dycc.errors.exceptions import ControllerError
from dycc.mvc._pathmapper import MultiTablePathMap, TreePathMap
from dycc.mvc.decorator import ControlFunction
from dycc import http

__author__ = 'Justus Adam'


class TestMapper(unittest.TestCase):
    def setUp(self):
        self.mt_mapper = MultiTablePathMap()
        self.t_mapper = TreePathMap()

        self.testpaths1 = (
            (
                'hello/bla',  lambda : 4, 'hello/bla', 4, ()
            ),
            (
                'hello/loko/nunu', lambda : 7, 'hello/loko/nunu', 7, ()
            ),
            (
                'tryi/{int}', lambda a: a, 'tryi/4', 4, (int, )
            ),
            (
                'tryit/**', lambda s: s, 'tryit/lolo', 'tryit/lolo', ()
            ),
            (
                '/', lambda : 4, '/', 4, ()
            )
        )

        self.testpaths2 = (
            (
                'horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch'), (int, )
            ),
        )

    def test_mt_add_path(self):

        method = 'get'
        host = 'localhost'
        port = 8080

        for path, handler, teststring, result, typeargs in self.testpaths1:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.mt_mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mt_mapper.find_handler(request)
            self.assertEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, typeargs in self.testpaths2:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.mt_mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mt_mapper.resolve(request)
            self.assertTupleEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, typeargs in self.testpaths1[0:2]:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.assertRaises(ControllerError, self.mt_mapper.add_path, path, handler)

    def test_t_add_path(self):
        method = 'get'
        host = 'localhost'
        port = 8080

        for path, handler, teststring, result, targs in self.testpaths1:
            handler = ControlFunction(handler, path, method, False, None)
            self.t_mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.t_mapper.find_handler(request)
            self.assertEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, targs in self.testpaths2:
            handler = ControlFunction(handler, path, method, False, None)
            self.t_mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.t_mapper.resolve(request)
            self.assertTupleEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, targs in self.testpaths1[0:2]:
            handler = ControlFunction(handler, path, method, False, None)
            self.assertRaises(ControllerError, self.t_mapper.add_path, path, handler)
