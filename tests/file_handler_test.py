__author__ = 'justusadam'

import unittest
from src.core.page_handlers import FileHandler


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.file_handler = FileHandler(['public', '..', '..'])

    def testFileAccess(self):
        self.assertEqual(self.file_handler.parse_path(), 403)


if __name__ == '__main__':
    unittest.main()
