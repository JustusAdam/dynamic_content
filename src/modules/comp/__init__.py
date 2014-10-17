from modules.comp import database_operations as dbo
from .config import CompConfig

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'

default_configuration = CompConfig


def prepare():
    ro = dbo.RegionOperations()
    ro.init_tables()
    ro.add_item_conf('start_menu', 'menu', 'commons', False, 0)
    ro.add_item('start_menu', 'navigation', 1, 'default_theme')
    ro.add_item('copyright', 'footer', 1, 'default_theme')
    ro.add_item_conf('copyright', 'com_text', 'commons', False, 0)


def add_commons_config(machine_name, commons_type, handler_module, show_title=True, access_type=0):
    dbo.RegionOperations().add_item_conf(machine_name, commons_type, handler_module, show_title, access_type)


def assign_common(common_name, region, weight, theme):
    dbo.RegionOperations().add_item(common_name, region, weight, theme)