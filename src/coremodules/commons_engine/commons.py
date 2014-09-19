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
        """
        Calls the database operation obtaining data about the menu items and casts them onto MenuItems for convenience
        :return:
        """
        db_result = self.mo.get_items(self.name)
        return [MenuItem(*a) for a in db_result]

    def get_menu_info(self):
        self.mo.get_menu_info(self.name)

    def order_items(self, items):
        """
        Takes a list of MenuItems and constructs a tree of parent items and child items.
        Child item lists are sored by weight
        :param items: List of MenuItems
        :return: Tree of MenuItems
        """
        mapping = {}
        for item in items:
            if item.parent_item in mapping:
                mapping[item.parent_item].append(item)
            else:
                mapping[item.parent_item] = [item]

        root = MenuItem('<root>', None, '/', None, 0)
        items.append(root)

        for item in items:
            if item.item_name in mapping:
                item.children = sorted(mapping[item.item_name], key=lambda s:s.weight)

        return root


class MenuItem:

    def __init__(self, item_name, display_name, item_path, parent_item, weight):
        self.item_name = item_name
        self.display_name = display_name
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = int(weight)
        self.children = []