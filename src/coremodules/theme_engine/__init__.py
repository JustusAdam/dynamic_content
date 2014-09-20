from . import database_operations as dbo

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'

from .themer import ThemeHandler

theme_handler = ThemeHandler


def prepare():
    dbo.RegionOperations().init_tables()