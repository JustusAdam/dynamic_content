from . import database_operations

__author__ = 'justusadam'


class CommonsHandler:

    def __init__(self, machine_name):
        self.name = machine_name


class MenuHandler(CommonsHandler):

    def __init__(self, machine_name):
        super().__init__(machine_name)

    def get_items(self):
        return database_operations.MenuOperations().get_items(self.name)