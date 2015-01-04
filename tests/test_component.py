import unittest
from dyc import core
from dyc.core._component import ComponentWrapper


__author__ = 'justusadam'


component_name = 'test_component'


@core.Component(component_name)
class Hello(object):
    attribute = None
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(core.get_component[component_name], ComponentWrapper)
        self.assertEqual(core.get_component[component_name].attribute, None)
        self.assertIsInstance(core.get_component[component_name]._wrapped, Hello)

        self.assertIs(core.get_component(component_name), core.get_component[component_name])