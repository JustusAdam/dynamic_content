import unittest
from dyc import dchp


class TestDcHP(unittest.TestCase):
    def test_parsing(self):
        with open(__file__.rsplit('/', 1)[0] + '/dchpsimple.html') as file:
            root = dchp.parser.parse(file.read())[0]
            print(root.content[-1])
