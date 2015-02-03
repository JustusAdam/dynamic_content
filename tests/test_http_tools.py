from dycc.http import headers
import inspect

__author__ = 'justusadam'
__version__ = '0.1'

import unittest


class TestHeaderConstruct(unittest.TestCase):
    def setUp(self):
        self.single_header_string_construct = headers.Header.from_str
        self.many_header_string_construct = headers.Header.many_from_str
        self.single_header_tuple_construct = headers.Header.from_list

    def test_string_construct(self):
        string = 'MyKey: SomeValue'
        string1 = 'MyKey: SomeValue\nOtherKey: AnotherValue'

        h = self.single_header_string_construct(string)

        self.assertIsInstance(h, headers.Header)
        self.assertEqual(h.key, 'MyKey')
        self.assertEqual(h.value, 'SomeValue')

        h2 = self.many_header_string_construct(string1)

        self.assertTrue(inspect.isgenerator(h2))

        h2 = tuple(h2)

        for i in h2:
            self.assertIsInstance(i, headers.Header)

        self.assertEqual(h2[0].key, 'MyKey')
        self.assertEqual(h2[0].value, 'SomeValue')

        self.assertEqual(h2[1].key, 'OtherKey')
        self.assertEqual(h2[1].value, 'AnotherValue')

    def test_tuple_construct(self):
        tuple1 = ('Key', 'Value')

        h = self.single_header_tuple_construct(tuple1)

        self.assertIsInstance(h, headers.Header)
        self.assertEqual(h.key, tuple1[0])
        self.assertEqual(h.value, tuple1[1])

class TestHeaderAutoConstruct(TestHeaderConstruct):
    def setUp(self):
        self.single_header_string_construct = self.many_header_string_construct = headers.Header.auto_construct
        self.single_header_tuple_construct = headers.Header.auto_construct


if __name__ == '__main__':
    unittest.main()
