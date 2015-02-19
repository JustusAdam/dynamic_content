import os
import unittest
import binascii
from framework.machinery import registry, component

__author__ = 'Justus Adam'
__version__ = '0.1'


class TestRegistry(unittest.TestCase):
    @component.inject_method(registry.Registry)
    def setUp(self, registry_dict):
        registry._Registry.create_table(fail_silently=True)
        self.registry = registry_dict
        self.r_db_obj = registry._Registry

    def test_int_store(self):
        good_values = dict(
            a=39485,
            b=0,
            c=9999999
        )

        for key, val in good_values.items():
            self.registry[key] = val

        for key, val in good_values.items():
            self.assertEqual(val, self.registry[key])

    def test_str_store(self):
        good_values = dict(
            f='string',
            e='',
            q='12456'
        )

        for key, val in good_values.items():
            self.registry[key] = val

        for key, val in good_values.items():
            self.assertEqual(self.registry[key], val)

    def test_list_store(self):
        vals = dict(
            a=['1', 2, 5],
            b=[],
            c=[[], 123, 'erger[]', '[]']
        )

        for key, val in vals.items():
            self.registry[key] = val

        for key, val in vals.items():
            self.assertListEqual(self.registry[key], val)

    def test_tuple_store(self):
        vals = dict(
            a=('1', 2, 5),
            b=(),
            c=([], 123, 'erger[]', '[]', ('8',))
        )

        for key, val in vals.items():
            self.registry[key] = val

        for key, val in vals.items():
            self.assertTupleEqual(self.registry[key], val)

    def test_dict_store(self):
        vals = dict(
            a={},
            b=dict(
                a=4,
                b=0,
                c='498tyhgonbe'
            ),
            c={
                3: 5,
                None: 'jvve'
            }
        )

        for key, val in vals.items():
            self.registry[key] = val

        for key, val in vals.items():
            self.assertDictEqual(self.registry[key], val)

    def test_keys(self):
        good_vals = {
            '': 6,
            'eirbv': 0,
            str(binascii.hexlify(os.urandom(126))): 'unimportant',
        }

        for key, val in good_vals.items():
            self.registry[key] = val

        for key, val in good_vals.items():
            self.assertEqual(val, self.registry[key])

        bad_values = {
            4: 8,
            0: 16,
            None: 5,
            str(binascii.hexlify(os.urandom(127))): 'unimportant',
            str(binascii.hexlify(os.urandom(130))): 'unimportant',
            frozenset(('fr', 'oo')): 'unimportant'
        }

        for key, val in bad_values.items():
            self.assertRaises(AssertionError, self.registry.__setitem__, key, val)

    def test_none_store(self):
        self.registry['key'] = None
        self.assertEqual(None, self.registry['key'])