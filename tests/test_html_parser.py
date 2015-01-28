import unittest
from dycc.util import parser
from dycc.util.parser import elements as _e


__author__ = 'Justus Adam'
__version__ = '0.1.1'


class TestParsing(unittest.TestCase):
    def test_simple_html(self):
        with open(__file__.rsplit('/', 1)[0] + '/simple.html') as file:
            root = parser.html.parse(file.read())[0]
            print(root)
            self.assertIsInstance(root, _e.Base)
            self.assertEqual(root.tag, 'html')

            self.assertIsInstance(root.children()[0], _e.Base)
            self.assertEqual(root.children()[0].tag, 'div')
            self.assertEqual(root.children()[0].text(), 'somecontent')

            self.assertIsInstance(root.children()[1], _e.Base)
            self.assertEqual(root.children()[1].tag, 'span')
            self.assertEqual(root.children()[1].text(), 'some more content')

            self.assertIsInstance(root.children()[2], _e.Base)
            self.assertEqual(root.children()[2].tag, 'div')

            self.assertIsInstance(root.children()[2].children()[0], _e.Base)
            self.assertEqual(root.children()[2].children()[0].tag, 'div')
            self.assertEqual(root.children()[2].children()[0].text(), 'hello')

            self.assertIsInstance(root.children()[3], _e.Base)
            self.assertEqual(root.children()[3].tag, 'a')
            self.assertEqual(root.children()[3].href, 'http://github.com')
            self.assertEqual(root.children()[3].text(), 'Github')


if __name__ == '__main__':
    unittest.main()
