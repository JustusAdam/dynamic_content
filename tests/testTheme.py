import os


__author__ = 'justusadam'

import unittest


class TestTheme(unittest.TestCase):
 def setUp(self):
  os.chdir('../src')


if __name__ == '__main__':
 unittest.main()
