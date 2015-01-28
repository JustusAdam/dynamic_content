import unittest
import dycc
from dycc._component import ComponentWrapper


__author__ = 'Justus Adam'


component_name = 'test_component'


@dycc.Component(component_name)
class Hello(object):
    attribute = None
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(dycc.get_component[component_name], ComponentWrapper)
        self.assertEqual(dycc.get_component[component_name].attribute, None)
        self.assertIsInstance(dycc.get_component[component_name]._wrapped, Hello)

        self.assertIs(dycc.get_component(component_name), dycc.get_component[component_name])