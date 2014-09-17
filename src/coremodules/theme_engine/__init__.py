__author__ = 'justusadam'

name = 'theme_engine'

role = 'theming_engine'

from .themer import ThemeHandler

theme_handler = ThemeHandler

def prepare():
    pass