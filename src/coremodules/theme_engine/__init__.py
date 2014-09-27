from . import database_operations as dbo

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'


def prepare():
 ro = dbo.RegionOperations()
 ro.init_tables()
 ro.add_item_conf('start_menu', 'menu', 'commons_engine', False)
 ro.add_item('start_menu', 'navigation', 1, 'default_theme')
 ro.add_item('copyright', 'footer', 1, 'default_theme')
 ro.add_item_conf('copyright', 'com_text', 'commons_engine', False)