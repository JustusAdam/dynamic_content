from .database_operations import AdminOperations
from .admin_pages import Overview, CategoryPage, SubcategoryPage
from core import Modules

__author__ = 'justusadam'

name = 'admin'


def content_handler(url, parent_handler):
  if not url.tail:
    handler = Overview
  elif len(url.tail) == 1:
    handler = CategoryPage
  elif len(url.tail) == 2:
    handler = SubcategoryPage
  else:
    handler_name = AdminOperations().get_page(url.tail[1])
    handler = Modules()[handler_name]
  return handler(url, parent_handler)


def prepare():
  ops = AdminOperations()

  ops.init_tables()

  from core.database_operations import ContentHandlers
  ContentHandlers().add_new('admin', 'admin', 'admin')