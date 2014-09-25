from . import database_operations
from framework.base_handlers import CommonsHandler
from framework.page import Component

__author__ = 'justusadam'


class TextCommonsHandler(CommonsHandler):

    com_type = 'text'

    def __init__(self, machine_name, show_title):
        self.co = database_operations.CommonsOperations()
        super().__init__(machine_name, show_title)

    def get_content(self, name):
        return self.co.get_content(name, self.com_type)

    @property
    def compiled(self):
        obj = Component(self.name, self.wrap_content(self.get_content(self.name)))
        return obj


