from .ar import Common
from dynct.modules.commons.ar import CommonsConfig

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'


def add_commons_config(machine_name, commons_type, handler_module, show_title=True, access_type=0):
    CommonsConfig(machine_name, commons_type, handler_module, show_title, access_type).save()


def assign_common(common_name, region, weight, theme):
    Common(common_name, region, weight, theme).save()