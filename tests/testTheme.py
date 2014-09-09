import os

from core.page import Page



__author__ = 'justusadam'

import unittest


class TestTheme(unittest.TestCase):

    def setUp(self):
        os.chdir('../src')



if __name__ == '__main__':
    unittest.main()
