from core import handlers
from .database_operations import Pages

__author__ = 'justusadam'


class Overview(handlers.content.Content):
  permission = 'access iris content overview'

  def process_content(self):
    pass

  def page_types(self):
    return ['iris']