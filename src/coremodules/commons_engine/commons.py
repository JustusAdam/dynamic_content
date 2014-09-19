from . import database_operations

__author__ = 'justusadam'


class CommonsHandler:

    def __init__(self, machine_name):
        self.name = machine_name


class MenuHandler(CommonsHandler):

    def __init__(self, machine_name):
        self.mo = database_operations.MenuOperations()
        super().__init__(machine_name)


    def get_items(self):
        db_result = self.mo.get_items(self.name)
        return [MenuItem(*a) for a in db_result]

    def get_menu_info(self):
        self.mo.get_menu_info(self.name)

    def order_items(self, items):
        parents = set([a.parent_item for a in items])
        root = MenuItem('<root>', 'NONE', '/', None, 0)

class MenuItem:

    def __init__(self, item_name, display_name, item_path, parent_item, weight):
        self.item_name = item_name
        self.display_name = display_name
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = int(weight)
        self.children = []