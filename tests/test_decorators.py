from dynct.modules.comp.decorator import Autoconf, Config
from dynct.util.misc_decorators import implicit, for_method_and_func

__author__ = 'justusadam'

import unittest


test = 'hello'

@implicit(test)
def testthing(f, t):
    print(f)
    print(t)


@implicit(test)
class testclass:
    def __init__(self, f):
        print(f)




class MyTestCase(unittest.TestCase):
    def test_something(self):
        testthing('blaa')

    def test_method_func(self):
        def lala(*args, **kwargs):
            print(*args + tuple(kwargs.values()))
            return args, kwargs


        def testfunc(a, b, c=0):
            print(a,b,c)

        class Tetst:

            def tsjvn(self, a,b,c='p'):
                print(a,b,c)
        a = Tetst().tsjvn
        for_method_and_func(lala)(testfunc)('test', 'func works')
        a('testclass', 'works', 8)


class ClassDecorator:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print('class', *args)
        return self.func(*args, **kwargs)


def function_decorator(func):
    def wrap(*args, **kwargs):
        print('function', *args)
        return func(*args, **kwargs)
    return wrap


class ClassDecWithArgs:
    def __init__(self, *args):
        self.args = args

    def __call__(self, some, *args):
        print(args)
        def wrap(*args):
            return some(*args)
        return wrap


class TestClass:
    @ClassDecorator
    def test1(self, *args):
        print(*args)


    @function_decorator
    def test2(self, *args):
        print(*args)

    @Autoconf(Config())
    def test3(self, *args):
        print(*args)


class TestDec(unittest.TestCase):
    def test_with_class(self):
        TestClass().test1('test1')

    def test_with_func(self):
        TestClass().test2('test2')

    def test_with_args(self):
        TestClass().test3('test3', 'test')







if __name__ == '__main__':

    unittest.main()


