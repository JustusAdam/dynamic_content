from dycc.util.typesafe import typesafe

__author__ = 'Justus Adam'

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):

        @typesafe
        def a(c:str='', b:str='') -> str:
            return c + b

        @typesafe
        def f(j, k:str='') -> str:
            return j

        c, b = 'hello', 'you'

        self.assertEqual(a(c,b), c + b)
        self.assertRaises(TypeError, a, (c,1))

        self.assertEqual(f('g'), 'g')
        self.assertRaises(TypeError, f, 2)


if __name__ == '__main__':
    unittest.main()
