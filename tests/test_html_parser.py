import unittest
import sys
from dyc.util import parser


__author__ = 'Justus Adam'
__version__ = '0.1'


class TestParsing(unittest.TestCase):
    def test_simple_html(self):
        with open(__file__.rsplit('/', 1)[0] + '/simple.html') as file:
            print(parser.html.parse(file.read()))


if __name__ == '__main__':
    unittest.main()
