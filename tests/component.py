import unittest
from dynct import core


__author__ = 'justusadam'


component_name = 'test_component'


@core.Component(component_name)
class Hello(object):
    pass


class ComponentTest(unittest.TestCase):
    def test_register(self):
        self.assertIsInstance(core.get_component[component_name], Hello)

        self.assertIs(core.get_component(component_name), core.get_component[component_name])