from .commons import TextCommons
from .menus import Handler
from .admin import MenuAdminController
from . import ar

__author__ = 'justusadam'

name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type):
    handlers = {
        'menu': Handler,
        'com_text': TextCommons
    }
    return handlers[item_type]


def prepare():

    ar.MenuItem('welcome', '/iris/1', 'start_menu', True, '<root>', 1).save()
    ar.MenuItem('welcome', '/iris/1', 'start_menu', True, '<root>', 1).save()
    ar.MenuItem('testpage', '/iris/2', 'start_menu', True, '<root>', 2).save()
    ar.MenuItem('setup', '/setup', 'start_menu', True, 'welcome', 1).save()
    ar.com('text')('copyright', '<p>\"dynamic_content\" CMS - © Justus Adam 2014</p>').save()