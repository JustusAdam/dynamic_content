__author__ = 'Justus Adam'

import unittest
from dyc.util import rest


class TestRestUtil(unittest.TestCase):
    def test_list_transform(self):
        testlist = [
            '4',
            9,
            'hello'
        ]
        expected = '["4", 9, "hello"]'
        self.assertEqual(rest.json_transform(testlist), expected)

        class CustomClass(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        testobj = CustomClass(jk='lolo', num=8, __test__=700)

        transformed = rest.json_transform(testobj)
        self.assertIn('"jk": "lolo"', transformed)
        self.assertIn('"num": 8', transformed)
        self.assertNotIn('"__test__": 700', transformed)


if __name__ == '__main__':
    unittest.main()
