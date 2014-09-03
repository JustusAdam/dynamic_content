import os
from coremodules.aphrodite.page import Page
from coremodules.aphrodite.themer import Theme

__author__ = 'justusadam'

import unittest


class TestTheme(unittest.TestCase):

    def setUp(self):
        os.chdir('../src')

    def test_Theme_class(self):
        themeClass = Theme(Page)
        self.assertEqual(themeClass.get_theme_path(), 'themes/default_theme')


if __name__ == '__main__':
    unittest.main()
