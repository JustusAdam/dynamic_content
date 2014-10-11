__author__ = 'justusadam'

import unittest

from core.handlers.file import FileHandler


class MyTestCase(unittest.TestCase):
  def setUp(self):
    self.file_handler = FileHandler(['public', '..', '..'])

  def testFileAccess(self):
    self.assertRaises(PermissionError, self.file_handler.parse_path)


if __name__ == '__main__':
  unittest.main()
