from .ar import CommonsConfig, Common

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'


def add_commons_config(machine_name, commons_type, handler_module, show_title=True, access_type=0):
    CommonsConfig(machine_name, commons_type, handler_module, show_title, access_type).save()


def assign_common(common_name, region, weight, theme):
    Common(common_name, region, weight, theme).save()

def prepare():
    add_commons_config('start_menu', 'menu', 'commons', False, 0)
    assign_common('start_menu', 'navigation', 1, 'default_theme')
    assign_common('copyright', 'footer', 1, 'default_theme')
    add_commons_config('copyright', 'com_text', 'commons', False, 0)
