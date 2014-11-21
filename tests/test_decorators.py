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


if __name__ == '__main__':
    unittest.main()
