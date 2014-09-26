from .commons import TextCommonsHandler
from . import database_operations as dbo
from coremodules.commons_engine.menus import MenuHandler
from coremodules.internationalization.database_operations import DisplayNamesOperations
from core import InitMod

__author__ = 'justusadam'


name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type, item_name, show_title, user, access_group):
    handlers = {
        'menu': MenuHandler,
        'com_text': TextCommonsHandler
    }
    return handlers[item_type](item_name, show_title, user, access_group)


class InitComEng(InitMod):

    operations = {
        'menu': dbo.MenuOperations,
        'common': dbo.CommonsOperations
    }

    def fill_tables(self, ops):
        ops['menu'].add_menu('start_menu', 'Start Menu', True)
        ops['menu'].add_menu_item('welcome', 'Welcome', '/iris/1', 'start_menu', True, '<root>', 1)
        ops['menu'].add_menu_item('testpage', 'Hello World', '/iris/2', 'start_menu', True, '<root>', 2)
        ops['menu'].add_menu_item('setup', 'Restart Setup', '/setup', 'start_menu', True, 'welcome', 1)
        ops['common'].add_content('text', 'copyright', '<p>_jaide CMS - © Justus Adam 2014</p>')

        do = DisplayNamesOperations()

        do.add_item('welcome', 'menu_items', ('english', 'Welcome'))
        do.add_item('testpage', 'menu_items', ('english', 'XKCD'))
        do.add_item('setup', 'menu_items', ('english', 'Restart Setup'))


init_class = InitComEng