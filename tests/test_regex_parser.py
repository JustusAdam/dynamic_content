import unittest

from dynct.core.mvc.controller import Controller

__author__ = 'justusadam'


class Test(unittest.TestCase):

    def test_regex(self):
        c = Controller()

        c.test('hello/f')