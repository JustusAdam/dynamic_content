from dynct.util.misc_decorators import implicit

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


class test2(testclass):
    def __init__(self):
        super().__init__()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        testthing('blaa')
        testclass()
        test2()


if __name__ == '__main__':
    unittest.main()
