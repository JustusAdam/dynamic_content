from .commons import database_operations
from core import handlers
from modules.comp.html_elements import ContainerElement, List

__author__ = 'justusadam'


class MenuItem:
    """
    MenuItem base implementation.

    A MenuItem represents a node in a menu and all its children and offers a method to render the menu/node by calling
    the render method in its children. The __str__ method returns a pure String representation of the rendered menu.

    Please note that the return of this function is flat and is simply a ordered list and child items are not wrapped
    in a list.
    """

    def __init__(self, item_name, display_name, item_path, parent_item, weight):
        self.item_name = item_name
        self.display_name = display_name
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = int(weight)
        self.children = []

    def render(self, depth=0):
        return (self.render_self(depth)) + self.render_children(depth + 1)

    def render_self(self, depth):
        if depth == 0:
            return '<' + self.display_name + '>'
        else:
            return '-' * depth + '  ' + self.display_name

    def render_children(self, depth=0):
        if not self.children:
            return ''
        else:
            return (a.render() for a in self.children)

    def __str__(self):
        return ''.join(str(a) for a in self.render(0))


class HTMLMenuItem(MenuItem):
    """
    MenuItem implementation that overrides the render methods to render into a HTML Menu.

    Note that the return value of the render method here is a tuple with one element for the title and one element for
    the list of children. aka. (title, children:List)
    """

    def render_self(self, depth):
        if self.item_path:
            return ContainerElement(self.display_name, html_type='a', classes={'layer-' + str(depth), 'menu'},
                                    element_id=self.item_name, additionals={'href': self.item_path})
        else:
            return ContainerElement(self.display_name, html_type='span', classes={'layer-' + str(depth), 'menu'},
                                    element_id=self.item_name)

    def render_children(self, depth=0):
        if not self.children:
            return ''
        return List(*[a.render(depth) for a in self.children], list_type='ul', item_classes='layer-' + str(depth),
                    classes=['layer-' + str(depth), 'menu'])

    def render(self, depth=0):
        return self.render_self(depth), self.render_children(depth + 1)


class Handler(handlers.common.Commons):
    source_table = 'menu_items'

    def __init__(self, machine_name, show_title, access_type, client):
        self.mo = database_operations.MenuOperations()
        super().__init__(machine_name, show_title, access_type, client)

    def get_items(self, item_class=MenuItem):
        """
        Calls the database operation obtaining data about the menu items and casts them onto MenuItems for convenience
        :return: List of MenuItems
        """
        db_result = self.mo.get_items(self.name)
        return [item_class(a[0], self.get_display_name(a[0], self.language), *a[1:]) for a in db_result]

    def order_items(self, items, root_class=MenuItem):
        """
        Takes a list of MenuItems and constructs a tree of parent items and child items.
        Child item lists are sored by weight
        :param items: List of MenuItems
        :return: Root for menu tree
        """
        mapping = {}
        root = root_class('<root>', self.get_display_name(self.name), '/', None, 0)

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
                    item.children = sorted(mapping[item.item_name], key=lambda s: s.weight)
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

    def menu(self, item_class=MenuItem):
        return self.order_items(self.get_items(item_class), item_class)

    def get_content(self, name):
        ul_list = self.menu(HTMLMenuItem).render_children(0)
        ul_list.element_id = name
        return ul_list
