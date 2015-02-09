from dynamic_content.http import headers
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
            hs = h.from_str(string)
            self.assertEqual(h, hs)
            self.assertEqual(hash(h), hash(hs))

        h2l = (self.many_header_string_construct(string1),
               self.any_header_string_construct(string1))

        for hs in h2l:
            self.assertTrue(inspect.isgenerator(hs))

            hs = tuple(hs)

            for i in hs:
                self.assertIsInstance(i, headers.Header)

            h1, h2 = hs

            self.assertEqual(h1.key, 'MyKey')
            self.assertEqual(h1.value, 'SomeValue')
            h3 = h1.from_str(str(h1))
            self.assertEqual(h1, h3)
            self.assertEqual(hash(h1), hash(h3))

            self.assertEqual(h2.key, 'OtherKey')
            self.assertEqual(h2.value, 'AnotherValue')
            h3 = h2.from_str(str(h2))
            self.assertEqual(h2, h3)
            self.assertEqual(hash(h2), hash(h3))

    def test_tuple_construct(self):
        tuple1 = ('Key', 'Value')

        h = self.single_header_tuple_construct(tuple1)

        self.assertIsInstance(h, headers.Header)
        self.assertEqual(h.key, tuple1[0])
        self.assertEqual(h.value, tuple1[1])
        h2 = h.from_str(str(h))
        self.assertEqual(h2, h)
        self.assertEqual(hash(h), hash(h2))


class TestHeaderAutoConstruct(TestHeaderConstruct):
    def setUp(self):
        self.single_header_string_construct = self.many_header_string_construct = self.any_header_string_construct = headers.Header.auto_construct
        self.single_header_tuple_construct = headers.Header.auto_construct

    def test_unsupported_type(self):
        for t in (
            True, 0, Exception()
        ):
            self.assertRaises(TypeError, headers.Header.auto_construct, t)


class TestHeaderComparison(unittest.TestCase):
    def test_equal(self):
        for k, v, o, ov in (
            ('MyKey', 'MyValue', 'OtherKey', 'OtherValue'),
            ('TestKey', 'testValue', 'Coollision', '88494y204')
        ):

            h1 = headers.Header(k, v)

            self.assertEqual(h1, headers.Header.from_tuple((k,v)))
            self.assertEqual(h1, headers.Header.from_str(k + ': ' + v))
            self.assertIn(h1, headers.Header.many_from_dict({k:v}))

            self.assertTrue(h1 == k + ': ' + v)
            self.assertTrue(h1 == (k, v))
            self.assertFalse(h1 == o + ': ' + ov)
            self.assertFalse(h1 == (o, ov))



if __name__ == '__main__':
    unittest.main()
