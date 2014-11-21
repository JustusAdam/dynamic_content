__author__ = 'justusadam'

import unittest
from dynct.util.misc_decorators import typesafe


class MyTestCase(unittest.TestCase):
    def test_something(self):

        @typesafe
        def a(c:str='', b:str='') -> str:
            return ''

        a(b='')



if __name__ == '__main__':
    unittest.main()
