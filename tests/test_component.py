import unittest
from framework import component


__author__ = 'Justus Adam'


component_name = 'test_component'


@component.Component(component_name)
class Hello(object):
    attribute = None
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(
            component.get_component[component_name], component.ComponentWrapper
        )
        self.assertEqual(
            component.get_component[component_name].attribute, None
        )
        self.assertIsInstance(
            component.get_component[component_name]._wrapped, Hello
        )

        self.assertIs(
            component.get_component(component_name),
            component.get_component[component_name]
        )