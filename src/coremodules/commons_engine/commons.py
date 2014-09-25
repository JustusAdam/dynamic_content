from . import database_operations
from framework.base_handlers import CommonsHandler

__author__ = 'justusadam'


class TextCommonsHandler(CommonsHandler):

    com_type = 'text'

    def __init__(self, machine_name, show_title):
        self.co = database_operations.CommonsOperations()
        super().__init__(machine_name, show_title)

    def get_content(self, name):
        return self.co.get_content(name, self.com_type)