from dycc.http import headers
import inspect

__author__ = 'justusadam'
__version__ = '0.1'

import unittest


class TestHeaderConstruct(unittest.TestCase):
    def setUp(self):
        self.single_header_string_construct = headers.Header.from_str
        self.any_header_string_construct = headers.Header.any_from_str
        self.many_header_string_construct = headers.Header.many_from_str
        self.single_header_tuple_construct = headers.Header.from_list

    def test_string_construct(self):
        string = 'MyKey: SomeValue'
        string1 = 'MyKey: SomeValue\nOtherKey: AnotherValue'

        hl = (self.single_header_string_construct(string),
              self.any_header_string_construct(string))
        for h in hl:
            self.assertIsInstance(h, headers.Header)
            self.assertEqual(h.key, 'MyKey')
            self.assertEqual(h.value, 'SomeValue')

        h2l = (self.many_header_string_construct(string1),
               self.any_header_string_construct(string1))

        for h2 in h2l:
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
        self.single_header_string_construct = self.many_header_string_construct = self.any_header_string_construct = headers.Header.auto_construct
        self.single_header_tuple_construct = headers.Header.auto_construct

    def test_unsupported_type(self):
        for t in (
            True, 0, Exception()
        ):
            self.assertRaises(TypeError, headers.Header.auto_construct, t)



if __name__ == '__main__':
    unittest.main()
