import unittest
import sys
from dyc.util import parser
from dyc.util.parser import elements as _e


__author__ = 'Justus Adam'
__version__ = '0.1.1'


class TestParsing(unittest.TestCase):
    def test_simple_html(self):
        with open(__file__.rsplit('/', 1)[0] + '/simple.html') as file:
            root = parser.html.parse(file.read())[0]
            print(root)
            self.assertIsInstance(root, _e.Base)
            self.assertEqual(root.name, 'html')

            self.assertIsInstance(root.children()[0], _e.Base)
            self.assertEqual(root.children()[0].name, 'div')
            self.assertEqual(root.children()[0].text(), 'somecontent')

            self.assertIsInstance(root.children()[1], _e.Base)
            self.assertEqual(root.children()[1].name, 'span')
            self.assertEqual(root.children()[1].text(), 'some more content')

            self.assertIsInstance(root.children()[2], _e.Base)
            self.assertEqual(root.children()[2].name, 'div')

            self.assertIsInstance(root.children()[2].children()[0], _e.Base)
            self.assertEqual(root.children()[2].children()[0].name, 'div')
            self.assertEqual(root.children()[2].children()[0].text(), 'hello')

            self.assertIsInstance(root.children()[3], _e.Base)
            self.assertEqual(root.children()[3].name, 'a')
            self.assertEqual(root.children()[3].href, 'http://github.com')
            self.assertEqual(root.children()[3].text(), 'Github')


if __name__ == '__main__':
    unittest.main()
