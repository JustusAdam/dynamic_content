__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from . import database_operations as dbo

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    return Modules()


def prepare():
    dbo.ContentHandlers().init_tables()
    dbo.Alias().init_tables()
    dbo.Modules().init_tables()