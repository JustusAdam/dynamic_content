import collections

from dycc import mvc
from dycc import http
from dycc.util import html
from dycm import commons, node
from dycm.users import decorator as user_dec
from . import model

__author__ = 'Justus Adam'

ADMIN_PATH = '/admin'


@mvc.controller_function('admin', method=http.RequestMethods.GET, query=False)
@user_dec.authorize('access admin pages')
@node.make_node()
def overview(dc_obj):

    dc_obj.context['pageclasses'] = {'admin-menu', 'overview', 'admin-page'}
    dc_obj.config['theme'] = 'admin_theme'

    tree = order_tree(
        model.Category.select(), Category.from_db(model.Subcategory.select())
        )

    new_node = dict(
        title='Website Administration',
        content=render_categories(*tree)
    )
    return new_node


def render_categories(*subcategories, basepath=ADMIN_PATH, classes=set()):
    subcategories = tuple(a.render(basepath) for a in subcategories)
    if len(subcategories) == 1:
        return html.ContainerElement(*subcategories, classes=classes)
    else:
        half = len(subcategories) // 2
        return html.ContainerElement(
            html.ContainerElement(
                *subcategories[:half],
                classes={'left-column'}
                ),
            html.ContainerElement(
                *subcategories[half:],
                classes={'right-column'}
                ),
            classes=classes
        )


def order_tree(parents, children):
    mapping = collections.defaultdict(list)
    for item in children:
        mapping[item.parent.machine_name].append(item)
    return [Category(name=parent.machine_name,
                     display_name=parent.display_name,
                     sub=mapping.get(parent.machine_name, None))
            for parent in parents]


@commons.implements('admin_menu')
class OverviewCommon(commons.Handler):
    source_table = 'admin'

    @staticmethod
    def get_content(conf, render_args, client):
        subcategories = (
            str(
                a.render(ADMIN_PATH))
                for a in order_tree(model.Category.select(),
                    (
                        Category(
                            child.machine_name,
                            child.display_name,
                            child.category,
                            None
                            )
                        for child in model.Subcategory.select()
                        )
                    )
                )
        return ''.join(subcategories)


@mvc.controller_function(
    'admin/{str}',
    method=http.RequestMethods.GET,
    query=False
    )
@node.make_node()
def category(dc_obj, name):
    dc_obj.context['pageclasses'] = {'admin-menu', 'category'}
    dc_obj.config['theme'] = 'admin_theme'

    parent = model.Category.get(machine_name=name)

    children = Category.from_db(
        model.Subcategory.select().where(model.Subcategory.category == parent)
        )

    tree = order_tree([parent], children)

    new_node = dict(
        title=parent.display_name if parent.display_name else parent.machine_name,
        content=render_categories(*tree)
        )

    return new_node


@mvc.controller_function(
    'admin/{str}/{str}',
    method=http.RequestMethods.GET,
    query=False
    )
@node.make_node()
def subcategory(dc_obj, category_name,  name):
    dc_obj.context['pageclasses'] = {'admin-menu', 'subcategory'}
    dc_obj.config['theme'] = 'admin_theme'

    parent = model.Subcategory.get(
        machine_name=name,
        category=model.Category.get(machine_name=category_name)
        )

    children = Category.from_db(
        model.AdminPage.select().where(model.AdminPage.subcategory == parent)
        )

    tree = order_tree([parent], children)

    new_node = dict(
        title= (
            parent.display_name
            if parent.display_name
            else parent.machine_name
            ),
        content=render_categories(
            *tree,
            basepath='{}/{}'.format(ADMIN_PATH, category_name)
            )
        )

    return new_node


@mvc.controller_function(
    'admin/{str}/{str}/{str}',
    method=http.RequestMethods.GET,
    query=False
    )
def page(dc_obj, category_name, subcategory_name, page_name):
    pass


class Category:
    classes = {'category'}

    @classmethod
    def from_db(cls, objects):
        for item in objects:
            yield cls.from_db_obj(item)

    @classmethod
    def from_db_obj(cls, dbobj):
        if isinstance(dbobj, model.AdminPage):
            parent = dbobj.subcategory
        elif isinstance(dbobj, model.Subcategory):
            parent = dbobj.category
        elif isinstance(dbobj, model.Category):
            parent = None
        else:
            raise TypeError(
                'Expected type {}, {}, {} got {}'.format(
                    type(model.Category),
                    type(model.Subcategory),
                    type(model.AdminPage),
                    type(dbobj)
                    )
                )

        return cls(dbobj.machine_name, dbobj.display_name, parent, None)

    def __init__(self, name, display_name, parent=None, sub=None):
        self.name = name
        self.display_name = display_name
        self.sub = sub
        self.parent = parent

    def render(self, url_base):
        path = url_base + '/' + self.name
        title = html.ContainerElement(
            self.display_name,
            html_type='a',
            additional={'href': path},
            classes=self.classes
        )
        if not self.sub:
            return title
        else:
            l = (a.render(path) for a in self.sub)
            return html.ContainerElement(
                title,
                html.List(
                    *l
                )
            )
