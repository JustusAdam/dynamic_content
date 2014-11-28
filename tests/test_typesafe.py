from dynct.util.typesafe import typesafe

__author__ = 'justusadam'

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):

        @typesafe
        def a(c:str='', b:str='') -> str:
            return c + b

        c, b = 'hello', 'you'

        self.assertEqual(a(c,b), c + b)
        self.assertRaises(AssertionError, a, (c,1))



if __name__ == '__main__':
    unittest.main()
