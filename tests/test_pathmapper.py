import unittest

from dycc.errors.exceptions import ControllerError
from dycc.mvc._pathmapper import MultiTablePathMap, TreePathMap
from dycc.mvc.decorator import ControlFunction
from dycc import http

__author__ = 'Justus Adam'


class TestMultiTableMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = MultiTablePathMap()

    def test_add_path(self):


        testpaths = (
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
                'horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch'), (int, )
            )
        )

        method = 'get'
        host = 'localhost'
        port = 8080

        for path, handler, teststring, result, typeargs in testpaths[0:4]:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mapper.find_handler(request)
            self.assertEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, typeargs in testpaths[4:]:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mapper.resolve(request)
            self.assertTupleEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result, typeargs in testpaths[0:2]:
            handler = ControlFunction(handler, path, method, False, None)
            handler.typeargs = typeargs
            self.assertRaises(ControllerError, self.mapper.add_path, path, handler)


class TestTreeMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = TreePathMap()

    def test_add_path(self):


        testpaths = (
            (
                'hello/bla',  lambda : 4, 'hello/bla', 4
            ),
            (
                'hello/loko/nunu', lambda : 7, 'hello/loko/nunu', 7
            ),
            (
                'tryi/{int}', lambda a: a, 'tryi/4', 4
            ),
            (
                'tryit/**', lambda s: s, 'tryit/lolo', 'tryit/lolo'
            ),
            (
                'horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch')
            )
        )

        method = 'get'
        host = 'localhost'
        port = 8080

        for path, handler, teststring, result in testpaths[0:4]:
            handler = ControlFunction(handler, path, method, False, None)
            self.mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mapper.find_handler(request)
            self.assertEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result in testpaths[4:]:
            handler = ControlFunction(handler, path, method, False, None)
            self.mapper.add_path(path, handler)
            request = http.Request(host, port, teststring, method, None, None, False)
            handler, args, kwargs = self.mapper.resolve(request)
            self.assertTupleEqual(handler(*args, **kwargs), result)

        for path, handler, teststring, result in testpaths[0:2]:
            handler = ControlFunction(handler, path, method, False, None)
            self.assertRaises(ControllerError, self.mapper.add_path, path, handler)
