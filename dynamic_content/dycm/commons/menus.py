import collections
import itertools

from framework.util import html
from . import model
from . import base, component


__author__ = 'Justus Adam'


def menu_chooser(name='menu_chooser', **kwargs):
    menus = tuple(_menu_chooser_iterator())
    return html.Select(*tuple(itertools.chain(*menus)), name=name, **kwargs)


def _menu_chooser_iterator():
    yield ('none', 'None'),
    for single_menu in model.Menu.select():

        yield tuple(
            (single_menu.machine_name + '-' + a[0], a[1])
            for a in menu(
                name=single_menu.machine_name,
                item_class=MenuChooseItem
            ).render()
        )

root_ident = -1


class MenuItem:
    """
    MenuItem base implementation.

    A MenuItem represents a node in a menu and all its children
    and offers a method to render the menu/node by calling
    the render method in its children. The __str__ method returns a pure
    String representation of the rendered menu.

    Please note that the return of this function is flat and is simply
    an ordered list and child items are not wrapped

    in a list.
    """

    def __init__(self, display_name, item_path, parent_item, weight, item_id):
        self.display_name = display_name
        self.item_path = item_path
        parent_item = (
            parent_item.oid
            if isinstance(parent_item, model.MenuItem)
            else parent_item
            )
        self.parent_item = (
            parent_item
            if parent_item is None
            else int(parent_item)
            )
        self.weight = int(weight)
        self.children = []
        self.item_id = item_id

    def render(self, depth=0, max_depth=-1):
        if 0 <= max_depth <= depth:
            return self.render_self(depth),
        else:
            return (self.render_self(depth), ) + self.render_children(depth + 1, max_depth)

    def render_self(self, depth):
        if depth == 0:
            return self.display_name
        else:
            return '-' * depth + '  ' + self.display_name

    def render_children(self, depth=0, max_depth=-1):
        if not self.children:
            return ()
        else:
            return tuple(itertools.chain(
                *tuple(a.render(depth, max_depth) for a in self.children))
                )

    def __str__(self):
        return ''.join(str(a) for a in self.render(0))


class MenuChooseItem(MenuItem):
    def render_self(self, depth):
        return str(self.item_id), super().render_self(depth)


class HTMLMenuItem(MenuItem):
    """
    MenuItem implementation that overrides the render methods
     to render into a HTML Menu.

    Note that the return value of the render method here is a tuple
     with one element for the title and one element for
     the list of children. aka. (title, children:List)
    """

    def render_self(self, depth):
        if self.item_path:
            return html.ContainerElement(
                self.display_name,
                html_type='a',
                classes={'layer-' + str(depth), 'menu'},
                additional={'href': self.item_path}
                )
        else:
            return html.ContainerElement(
                self.display_name,
                html_type='span',
                classes={'layer-' + str(depth), 'menu'}
                )

    def render_children(self, depth=0, max_depth=-1):
        if not self.children:
            return ''
        return html.List(
            *tuple(a.render(depth, max_depth) for a in self.children),
            list_type='ul',
            item_classes={'layer-' + str(depth)},
            classes={'layer-' + str(depth), 'menu'}
            )

    def render(self, depth=0, max_depth=-1):
        if 0 <= max_depth <= depth:
            return self.render_self(depth)
        else:
            return self.render_self(depth), self.render_children(depth + 1, max_depth)


@component.implements('menu')
class Handler(base.Handler):
    type = 'menu'

    def get_content(self, conf, render_args, client):
        name = conf.machine_name
        if render_args is None:
            ul_list = menu(name, item_class=HTMLMenuItem)
            ul_list = ul_list.render_children(0)
        else:
            ul_list = menu(
                name,
                item_class=HTMLMenuItem).render_children(0, int(render_args)
                )
        if ul_list:
            ul_list.element_id = name
        return ul_list


def get_items(menu_i, item_class=MenuItem):
    """
    Calls the database operation obtaining data about the menu items
    and casts them onto MenuItems for convenience
    :return: List of MenuItems
    """
    menu_i = (
        model.Menu.get(machine_name=menu_i)
        if isinstance(menu_i, str)
        else menu_i
        )
    items = model.MenuItem.select().where(model.MenuItem.menu == menu_i,
                                          model.MenuItem.enabled == True)
    return (item_class(
        a.display_name,
        a.path,
        a.parent,
        a.weight,
        a.oid
    ) for a in items)


def order_items(name, source_table, language, items, root_class=MenuItem):
    """
    Takes a list of MenuItems and constructs a tree of parent items and child items.
    Child item lists are sored by weight
    :param items: List of MenuItems
    :return: Root for menu tree
    """
    mapping = collections.defaultdict(list)

    def order():
        """
        Implementation of the tree construction. Uses two loops. Child item lists are sorted
        :return:
        """

        for item in items:
            key = item.parent_item if item.parent_item else root_ident
            mapping[key].append(item)

        for item in items:
            item.children = sorted(
                mapping[item.item_id],
                key=lambda s: s.weight) if item.item_id in mapping else None
        return mapping[-1][0]

    return order()  


def menu(name, source_table='menu', language='english', item_class=MenuItem):
    return order_items(name, source_table, language, get_items(name, item_class), item_class)
