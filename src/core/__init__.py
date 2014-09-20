__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from . import database_operations as dbo

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    m = Modules()
    m.reload()
    return m


def prepare():
    dbo.ContentHandlers().init_tables()
    a = dbo.Alias()
    a.init_tables()
    a.add_alias('/iris/1', '/welcome')
    dbo.Modules().init_tables()
    dbo.ContentTypes().init_tables()