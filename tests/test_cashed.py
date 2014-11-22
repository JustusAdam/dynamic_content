from dynct.util.misc_decorators import cache
import unittest

__author__ = 'justusadam'



class Test(unittest.TestCase):

    def test_cashed(self):

        @cache
        def func(*args):
            print('executing func')
            return args

        value1 = ('hello', 'test')
        self.assertEqual(func(*value1), value1)
        self.assertEqual(func(), value1)
        value2 = ('new', 'values')
        self.assertEqual(func(*value2), value2)
        self.assertEqual(func(), value2)