import unittest
import sys
from dyc.util import parser
from dyc.util import html


__author__ = 'Justus Adam'
__version__ = '0.1.1'


class TestParsing(unittest.TestCase):
    def test_simple_html(self):
        with open(__file__.rsplit('/', 1)[0] + '/simple.html') as file:
            root = parser.html.parse(file.read())[0]
            print(root)
            self.assertIsInstance(root, html.ContainerElement)
            self.assertEqual(root.html_type, 'html')
            self.assertIsInstance(root.content[0], html.ContainerElement)
            self.assertEqual(root.content[0].html_type, 'div')
            self.assertEqual(root.content[0].content[0], 'somecontent')
            self.assertIsInstance(root.content[1], html.ContainerElement)
            self.assertEqual(root.content[1].html_type, 'span')
            self.assertEqual(root.content[1].content[0], 'some more content')
            self.assertIsInstance(root.content[2], html.ContainerElement)
            self.assertEqual(root.content[2].html_type, 'div')
            self.assertIsInstance(root.content[2].content[0], html.ContainerElement)
            self.assertEqual(root.content[2].content[0].html_type, 'div')
            self.assertEqual(root.content[2].content[0].content[0], 'hello')
            self.assertIsInstance(root.content[3], html.A)
            self.assertEqual(root.content[3].value_params['href'], 'http://github.com')
            self.assertEqual(root.content[3].content[0], 'Github')


if __name__ == '__main__':
    unittest.main()
