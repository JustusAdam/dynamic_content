import unittest
import dynamic_content
from dynamic_content._component import ComponentWrapper


__author__ = 'Justus Adam'


component_name = 'test_component'


@dynamic_content.Component(component_name)
class Hello(object):
    attribute = None
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(dynamic_content.get_component[component_name], ComponentWrapper)
        self.assertEqual(dynamic_content.get_component[component_name].attribute, None)
        self.assertIsInstance(dynamic_content.get_component[component_name]._wrapped, Hello)

        self.assertIs(dynamic_content.get_component(component_name), dynamic_content.get_component[component_name])