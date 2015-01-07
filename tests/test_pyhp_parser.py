import unittest
from dyc.util.parser import pyhp


class TestPyHP(unittest.TestCase):
    def test_parsing(self):
        with open(__file__.rsplit('/', 1)[0] + '/pyhpsimple.html') as file:
            root = pyhp.parse(file.read())[0]
            print(root.content[-1])
