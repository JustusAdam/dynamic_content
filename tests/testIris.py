__author__ = 'justusadam'

import unittest

from core.database import Database


class generalIrisTesting(unittest.TestCase):
    def setUp(self):
        from includes.global_vars import *
        db = Database()
        db.insert('iris', ('content_type', 'published', 'creator'), ('test_type', '0', 'test_user'))

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
