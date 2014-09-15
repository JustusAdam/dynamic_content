from .commons import MenuHandler, CommonsHandler

__author__ = 'justusadam'


name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type, item_name):
    handlers = {
        'menu': MenuHandler,
        'common': CommonsHandler
    }
    return handlers[item_type](item_name)