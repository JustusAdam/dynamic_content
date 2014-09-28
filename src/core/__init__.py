__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from . import database_operations as dbo
from . import admin, comp, form, users

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
  m = Modules()
  m.reload()
  return m


def add_content_handler(name, handler, prefix):
  dbo.ContentHandlers().add_new(name, handler, prefix)


def prepare():
  dbo.ContentHandlers().init_tables()
  a = dbo.Alias()
  a.init_tables()
  a.add_alias('/iris/1', '/welcome')
  mo = dbo.ModuleOperations()
  mo.init_tables()
  dbo.ContentTypes().init_tables()