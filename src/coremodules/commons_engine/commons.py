from . import database_operations

__author__ = 'justusadam'


class CommonsHandler:

    def __init__(self, machine_name, title):
        self.name = machine_name
        self.title = title


class MenuHandler(CommonsHandler):

    def __init__(self, machine_name, title):
        super().__init__(machine_name, title)

    def get_items(self):
        return database_operations.MenuOperations().get_items(self.name)