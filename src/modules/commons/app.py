from application.app import AppFragment
from .commons import TextCommons
from modules.commons.menus import Handler

__author__ = 'justusadam'


class CommonsApp(AppFragment):
    common_handlers = {
        'menu': Handler,
        'com_text': TextCommons
    }

    def common_handler(self, item_type):
        return self.common_handlers[item_type]

    def setup_fragment(self):
        from . import database_operations as dbo
        mo = dbo.MenuOperations()
        co = dbo.CommonsOperations()
        co.init_tables()
        mo.init_tables()

        mo.add_menu('start_menu', True)
        mo.add_menu_item('welcome', '/iris/1', 'start_menu', True, '<root>', 1)
        mo.add_menu_item('testpage', '/iris/2', 'start_menu', True, '<root>', 2)
        mo.add_menu_item('setup', '/setup', 'start_menu', True, 'welcome', 1)
        co.add_content('text', 'copyright', '<p>\"dynamic_content\" CMS - © Justus Adam 2014</p>')