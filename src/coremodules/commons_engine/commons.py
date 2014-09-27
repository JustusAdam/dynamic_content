from . import database_operations
from core.base_handlers import CommonsHandler

__author__ = 'justusadam'


class TextCommonsHandler(CommonsHandler):
 com_type = 'text'

 def __init__(self, machine_name, show_title, user, access_group):
  self.co = database_operations.CommonsOperations()
  super().__init__(machine_name, show_title, user, access_group)

 def get_content(self, name):
  return self.co.get_content(name, self.com_type)