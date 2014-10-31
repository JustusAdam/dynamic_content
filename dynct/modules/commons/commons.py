from . import database_operations
from dynct.core.handlers.common import Commons

__author__ = 'justusadam'


class TextCommons(Commons):
    com_type = 'text'

    def __init__(self, machine_name, show_title, access_type, client):
        self.co = database_operations.CommonsOperations()
        super().__init__(machine_name, show_title, access_type, client)

    def get_content(self, name):
        return self.co.get_content(name, self.com_type)