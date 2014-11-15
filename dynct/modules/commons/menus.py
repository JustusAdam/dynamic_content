import itertools
from dynct.modules.comp.html_elements import ContainerElement, List, Select
from dynct.modules import i18n
from . import ar
from .base import Commons

__author__ = 'justusadam'


def menu_chooser(name='menu_chooser', **kwargs):
    menus = [[('none', 'None')]] + [[(menu.element_name + '-' + a[0], a[1]) for a in MenuRenderer(menu.element_name).menu(MenuChooseItem).render()] for menu in ar.CommonsConfig.get_all(element_type='menu')]
    return Select(*list(itertools.chain(*menus)), name=name, **kwargs)


root_ident = -1


class MenuItem:
    """
    MenuItem base implementation.

    A MenuItem represents a node in a menu and all its children and offers a method to render the menu/node by calling
    the render method in its children. The __str__ method returns a pure String representation of the rendered menu.

    Please note that the return of this function is flat and is simply a ordered list and child items are not wrapped
    in a list.
    """

    def __init__(self, display_name, item_path, parent_item, weight, item_id):
        self.display_name = display_name
        self.item_path = item_path
        if parent_item is None:
            self.parent_item = parent_item
        else:
            self.parent_item = int(parent_item)
        self.weight = int(weight)
        self.children = []
        self.item_id = item_id

    def render(self, depth=0, max_depth=-1):
        if 0 <= max_depth <= depth:
            return [self.render_self(depth)]
        else:
            return [self.render_self(depth)] + self.render_children(depth + 1, max_depth)

    def render_self(self, depth):
        if depth == 0:
            return self.display_name
        else:
            return '-' * depth + '  ' + self.display_name

    def render_children(self, depth=0, max_depth=-1):
        if not self.children:
            return []
        else:
            return list(itertools.chain(*[a.render(depth, max_depth) for a in self.children]))

    def __str__(self):
        return ''.join(str(a) for a in self.render(0))


class MenuChooseItem(MenuItem):
    def render_self(self, depth):
        return str(self.item_id), super().render_self(depth)


class HTMLMenuItem(MenuItem):
    """
    MenuItem implementation that overrides the render methods to render into a HTML Menu.

    Note that the return value of the render method here is a tuple with one element for the title and one element for
    the list of children. aka. (title, children:List)
    """

    def render_self(self, depth):
        if self.item_path:
            return ContainerElement(self.display_name, html_type='a', classes={'layer-' + str(depth), 'menu'},
                                    additional={'href': self.item_path})
        else:
            return ContainerElement(self.display_name, html_type='span', classes={'layer-' + str(depth), 'menu'})

    def render_children(self, depth=0, max_depth=-1):
        if not self.children:
            return ''
        return List(*[a.render(depth, max_depth) for a in self.children], list_type='ul', item_classes={'layer-' + str(depth)},
                    classes={'layer-' + str(depth), 'menu'})

    def render(self, depth=0, max_depth=-1):
        if 0 <= max_depth <= depth:
            return self.render_self(depth)
        else:
            return self.render_self(depth), self.render_children(depth + 1, max_depth)


class Handler(Commons):
    source_table = 'menu_items'

    def get_content(self, name):
        renderer = MenuRenderer(self.name, self.language)
        if self.render_args is None:
            ul_list = renderer.menu(HTMLMenuItem).render_children(0)
        else:
            ul_list = renderer.menu(HTMLMenuItem).render_children(0, int(self.render_args))
        ul_list.element_id = name
        return ul_list


class MenuRenderer:
    source_table = 'menu_items'

    def __init__(self, name, language='english'):
        self.name = name
        self.language = language

    def get_items(self, item_class=MenuItem):
        """
        Calls the database operation obtaining data about the menu items and casts them onto MenuItems for convenience
        :return: List of MenuItems
        """
        items = ar.MenuItem.get_all(menu=self.name, enabled=True)
        return [item_class(
            a.display_name,
            a.item_path,
            a.parent_item,
            a.weight,
            a.item_id
        ) for a in items]

    def order_items(self, items, root_class=MenuItem):
        """
        Takes a list of MenuItems and constructs a tree of parent items and child items.
        Child item lists are sored by weight
        :param items: List of MenuItems
        :return: Root for menu tree
        """
        mapping = {}
        root = root_class(i18n.get_display_name(self.name, self.source_table, self.language), '/', 0, 0, root_ident)

        def order():
            """
            Implementation of the tree construction. Uses two loops. Child item lists are sorted
            :return:
            """
            def assign_to(key, val):
                if key in mapping:
                    mapping[key].append(val)
                else:
                    mapping[key] = [val]
            for item in items:
                if not item.parent_item:
                    assign_to(root_ident, item)
                else:
                    assign_to(item.parent_item, item)

            items.append(root)

            for item in items:
                if item.item_id in mapping:
                    item.children = sorted(mapping[item.item_id], key=lambda s: s.weight)
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