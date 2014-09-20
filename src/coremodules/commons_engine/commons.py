from . import database_operations
from framework.html_elements import List, ContainerElement
from framework.page import Component

__author__ = 'justusadam'


class CommonsHandler:

    def __init__(self, machine_name):
        self.name = machine_name

    @property
    def compiled(self):
        return None


class MenuHandler(CommonsHandler):

    def __init__(self, machine_name):
        self.mo = database_operations.MenuOperations()
        super().__init__(machine_name)
        self.menu_name = self.get_menu_info()


    def get_items(self):
        """
        Calls the database operation obtaining data about the menu items and casts them onto MenuItems for convenience
        :return:
        """
        db_result = self.mo.get_items(self.name)
        return [MenuItem(*a) for a in db_result]

    def get_menu_info(self):
        return self.mo.get_menu_info(self.name)

    def order_items(self, items):
        """
        Takes a list of MenuItems and constructs a tree of parent items and child items.
        Child item lists are sored by weight
        :param items: List of MenuItems
        :return: Root for menu tree
        """
        mapping = {}
        root = MenuItem('<root>', self.menu_name, '/', None, 0)

        def order():
            """
            Implementation of the tree construction. Uses two loops. Child item lists are sorted
            :return:
            """
            for item in items:
                if item.parent_item in mapping:
                    mapping[item.parent_item].append(item)
                else:
                    mapping[item.parent_item] = [item]


            items.append(root)

            for item in items:
                if item.item_name in mapping:
                    item.children = sorted(mapping[item.item_name], key=lambda s:s.weight)
            return root

        def alt_order():
            """
            Alternative implementation of the tree construction, uses only one loop, relies heavily on references.
            Child items lists are unsorted.
            :return:
            """
            for item in items:
                if item.item_name in mapping:
                    item.children = mapping[item.item_name]
                else:
                    mapping[item.item_name] = []
                if item.parent_item and item.parent_item in mapping:
                    mapping[item.parent_item].append(item)
                else:
                    mapping[item.parent_item] = [item]

            return root

        return order()

    @property
    def compiled(self):
        ul_list = self.order_items(self.get_items()).render_children(0)
        ul_list.element_id = self.name
        return Component(self.name, ul_list)


class MenuItem:

    def __init__(self, item_name, display_name, item_path, parent_item, weight):
        self.item_name = item_name
        self.display_name = display_name
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = int(weight)
        self.children = []

    def render(self, depth=0):
        return self.render_self(depth), self.render_children(depth+1)

    def render_self(self, depth):
        if self.item_path:
            return ContainerElement(self.display_name, html_type='a', classes={'layer-' + str(depth), 'menu'}, element_id=self.item_name, additionals={'href':self.item_path})
        else:
            return ContainerElement(self.display_name, html_type='span', classes={'layer-' + str(depth), 'menu'}, element_id=self.item_name)

    def render_children(self, depth=0):
        return List(*[a.render(depth + 1) for a in self.children], list_type='ul', item_classes='layer-' + str(depth + 1), classes=['layer-' + str(depth), 'menu'])

    def __str__(self):
        return ''.join(str(a) for a in self.render(0))