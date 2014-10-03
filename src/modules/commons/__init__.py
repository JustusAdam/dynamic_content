from .commons import TextCommons
from . import database_operations as dbo
from modules.commons.menus import Handler

__author__ = 'justusadam'

name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type, item_name, show_title, user, access_group):
  handlers = {
    'menu': Handler,
    'com_text': TextCommons
  }
  return handlers[item_type](item_name, show_title, user, access_group)


def prepare():
  mo = dbo.MenuOperations()
  co = dbo.CommonsOperations()
  co.init_tables()
  mo.init_tables()

  mo.add_menu('start_menu', True)
  mo.add_menu_item('welcome', '/iris/1', 'start_menu', True, '<root>', 1)
  mo.add_menu_item('testpage', '/iris/2', 'start_menu', True, '<root>', 2)
  mo.add_menu_item('setup', '/setup', 'start_menu', True, 'welcome', 1)
  co.add_content('text', 'copyright', '<p>\"dynamic_content\" CMS - © Justus Adam 2014</p>')

  # do = DisplayNamesOperations()

  # do.add_item('welcome', 'menu_items', ('english', 'Welcome'))
  #do.add_item('testpage', 'menu_items', ('english', 'XKCD'))
  #do.add_item('setup', 'menu_items', ('english', 'Restart Setup'))