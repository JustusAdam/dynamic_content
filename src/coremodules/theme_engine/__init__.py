from . import database_operations as dbo
from core import InitMod

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'


class InitThm(InitMod):
    operations = {
        'ro': dbo.RegionOperations
    }

    def fill_tables(self, ops):
        ops['ro'].add_item_conf('start_menu', 'menu', 'commons_engine', False)
        ops['ro'].add_item('start_menu', 'navigation', 1, 'default_theme')
        ops['ro'].add_item('copyright', 'footer', 1, 'default_theme')
        ops['ro'].add_item_conf('copyright', 'com_text', 'commons_engine', False)

init_class = InitThm