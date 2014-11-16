from .commons import TextCommons
from .menus import Handler
from .admin import MenuAdminController

__author__ = 'justusadam'

name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type):
    handlers = {
        'menu': Handler,
        'com_text': TextCommons
    }
    return handlers[item_type]