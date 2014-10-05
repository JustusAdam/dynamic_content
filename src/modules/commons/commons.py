from . import database_operations
from core import handlers

__author__ = 'justusadam'


class TextCommons(handlers.Commons):
  com_type = 'text'

  def __init__(self, machine_name, show_title, client):
    self.co = database_operations.CommonsOperations()
    super().__init__(machine_name, show_title, client)

  def get_content(self, name):
    return self.co.get_content(name, self.com_type)