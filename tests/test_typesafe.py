from dynct.util.typesafe import typesafe

__author__ = 'justusadam'

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):

        @typesafe
        def a(c:str='', b:str='') -> str:
            return ''

        self.assertEqual(a(b='jutu'))



if __name__ == '__main__':
    unittest.main()
