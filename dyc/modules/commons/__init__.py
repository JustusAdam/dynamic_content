from . import commons, menus, admin
from .component import register, implements
from .base import Handler

__author__ = 'justusadam'


def common_handler(item_type):
    handlers = {
        'menu': menus.Handler,
        'com_text': commons.TextCommons
    }
    return handlers[item_type]