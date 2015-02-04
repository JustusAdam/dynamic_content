import unittest
from dycc.errors.exceptions import ControllerError, MethodHandlerNotFound
from dycc.route._map import MultiTablePathMap, TreePathMap
from dycc.route.decorator import ControlFunction
from dycc import http

__author__ = 'Justus Adam'


class TestMapper(unittest.TestCase):
    def setUp(self):
        self.mt_mapper = MultiTablePathMap()
        self.t_mapper = TreePathMap()

        self.testpaths1 = (
            ('hello/bla',  lambda : 4, 'hello/bla', 4, ()),
            ('hello/loko/nunu', lambda : 7, 'hello/loko/nunu', 7, ()),
            ('tryi/{int}', lambda a: a, 'tryi/4', 4, (int, )),
            ('tryit/**', lambda s: s, 'tryit/lolo', 'tryit/lolo', ()),
            ('/', lambda : 4, '/', 4, ())
        )

        self.testpaths2 = (
            ('horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch'), (int, )),
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

    def test_header_resolving(self):
        host = 'localhost'
        port = 0
        query = ()


        for mapper in (self.t_mapper, self.mt_mapper):

            for function, path, method, headers, is_empty in (
                (lambda :7, '/test', 'get', frozenset(http.headers.Header.auto_construct('Location: /\nHTTPS: None')), False),
                (lambda : 0, '/', 'post', frozenset((http.headers.Header.auto_construct('Location: hello'),)), False),
                (lambda : 9, '/lala', 'get', frozenset(), True)
            ):

                handler = ControlFunction(
                    function=function, value=path, method=method, headers=headers, query=query
                )

                mapper.add_path(path, handler)
                request1 = http.Request(host, port, path, method, query, frozenset(), False)
                request2 = http.Request(host, port, path, method, query, headers, False)
                h2 = http.headers.HeaderMap(headers, Method='0')
                request3 = http.Request(host, port, path, method, query, h2, False)
                if not is_empty:
                    self.assertRaises(MethodHandlerNotFound, mapper.resolve, request1)
                self.assertIs(
                    mapper.resolve(request2)[0].function, function
                )
                if not is_empty:
                    self.assertRaises(MethodHandlerNotFound, mapper.resolve, request3)