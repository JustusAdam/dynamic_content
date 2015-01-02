import unittest

from dyc.errors.exceptions import ControllerError
from dyc.core.mvc._pathmapper import MultiTablePathMap, TreePathMap
from dyc.core.mvc.decorator import ControlFunction

__author__ = 'justusadam'


class TestMultiTableMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = MultiTablePathMap()

    def test_add_path(self):


        testpaths = [
            [
                'hello/bla',  lambda : 4, 'hello/bla', 4, ()
            ],
            [
                'hello/loko/nunu', lambda : 7, 'hello/loko/nunu', 7, ()
            ],
            [
                'tryi/{int}', lambda a: a, 'tryi/4', 4, (int, )
            ],
            [
                'tryit/**', lambda s: s, 'tryit/lolo', 'tryit/lolo', ()
            ],
            [
                'horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch'), (int, )
            ]
        ]

        method = 'get'

        for path, handler, teststring, result, typeargs in testpaths[0:4]:
            handler = ControlFunction(handler, path, method, False)
            handler.typeargs = typeargs
            self.mapper.add_path(path, handler)
            self.assertEqual(self.mapper.get_handler(teststring, method)(), result)

        for path, handler, teststring, result, typeargs in testpaths[4:]:
            handler = ControlFunction(handler, path, method, False)
            handler.typeargs = typeargs
            self.mapper.add_path(path, handler)
            self.assertTupleEqual(self.mapper.get_handler(teststring, method)(), result)

        for path, handler, teststring, result, typeargs in testpaths[0:2]:
            handler = ControlFunction(handler, path, method, False)
            handler.typeargs = typeargs
            self.assertRaises(ControllerError, self.mapper.add_path, path, handler)


class TestTreeMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = TreePathMap()

    def test_add_path(self):


        testpaths = [
            [
                'hello/bla',  lambda : 4, 'hello/bla', 4
            ],
            [
                'hello/loko/nunu', lambda : 7, 'hello/loko/nunu', 7
            ],
            [
                'tryi/{int}', lambda a: a, 'tryi/4', 4
            ],
            [
                'tryit/**', lambda s: s, 'tryit/lolo', 'tryit/lolo'
            ],
            [
                'horn/{int}/tee/**', lambda a, b: (a,b), 'horn/4/tee/tree/branch', (4,'horn/4/tee/tree/branch')
            ]
        ]

        method = 'get'

        for path, handler, teststring, result in testpaths[0:4]:
            self.mapper.add_path(path, handler)
            self.assertEqual(self.mapper.get_handler(teststring, method)(), result)

        for path, handler, teststring, result in testpaths[4:]:
            self.mapper.add_path(path, handler)
            self.assertTupleEqual(self.mapper.get_handler(teststring, method)(), result)

        for path, handler, teststring, result in testpaths[0:2]:
            self.assertRaises(ControllerError, self.mapper.add_path, path, handler)