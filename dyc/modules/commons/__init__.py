from . import commons, menus, admin, base
from .component import register

__author__ = 'justusadam'

name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type):
    handlers = {
        'menu': menus.Handler,
        'com_text': commons.TextCommons
    }
    return handlers[item_type]