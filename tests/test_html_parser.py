import unittest
import sys
from dyc.util.parser import html


class TestParsing(unittest.TestCase):
    def test_simple_html(self):
        with open(__file__.rsplit('/', 1)[0] + '/simple.html') as file:
            print(html_parser.parse(file.read()))


if __name__ == '__main__':
    unittest.main()
