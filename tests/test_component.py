import unittest
import dyc
from dyc._component import ComponentWrapper


__author__ = 'Justus Adam'


component_name = 'test_component'


@dyc.Component(component_name)
class Hello(object):
    attribute = None
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(dyc.get_component[component_name], ComponentWrapper)
        self.assertEqual(dyc.get_component[component_name].attribute, None)
        self.assertIsInstance(dyc.get_component[component_name]._wrapped, Hello)

        self.assertIs(dyc.get_component(component_name), dyc.get_component[component_name])