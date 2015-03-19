import unittest
from framework.machinery import component


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
            component.get_component[component_name].get().attribute, None
        )
        self.assertIsInstance(
            component.get_component[component_name].get(), Hello
        )

        self.assertIs(
            component.get_component(component_name).get(),
            component.get_component[component_name].get()
        )