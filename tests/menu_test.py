from modules.commons.database_operations import MenuOperations
from modules.comp.database_operations import RegionOperations

__author__ = 'justusadam'

import unittest


class TestMenu(unittest.TestCase):
  def setUp(self):
    self.mo = MenuOperations()
    self.ro = RegionOperations()

    self.mo.add_menu('test_menu', True)
    self.mo.add_menu_item('welcome', 'Welcome', '/iris/1', 'test_menu', True, '<root>', 1)
    self.mo.add_menu_item('940', 'hello world', '/iris/1', 'test_menu', True, '<root>', 2)
    self.mo.add_menu_item('667', 'lorem ipsum', '/setup', 'test_menu', True, 'welcome', 1)
    self.mo.add_menu_item('9098', 'setup', '/setup', 'test_menu', False, 'welcome', 4)
    self.mo.add_menu_item('5657', 'tralila', '/iris/1', 'test_menu', True, 'welcome', 6)
    self.mo.add_menu_item('000', '8903-', '/iris/2', 'test_menu', True, '<root>', 3)
    self.mo.add_menu_item('4444', 'jutuse', '/iris/1', 'other_menu', True, '<root>', 8)
    self.mo.add_menu_item('6368', 'naunau', 'nau', 'test_menu', True, '940', 3)

    self.ro.add_item_conf('test_menu', 'menu', 'commons_engine')
    self.ro.add_item('test_menu', 'navigation', 1, 'default_theme')

  #
  # def test_something(self):
  #   menu_handler = MenuHandler('test_menu')
  #   self.mo.disable_item('9098', 'test_menu')
  #   root = menu_handler.order_items(menu_handler.get_items())
  #   self.mo.enable_item('9098', 'test_menu')
  #   root = menu_handler.order_items(menu_handler.get_items())
  #   print('done')


if __name__ == '__main__':
  unittest.main()
