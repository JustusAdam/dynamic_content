import collections

from dynct.core import mvc
from dynct import dchttp
from dynct.modules.comp import decorator as comp_dec
from dynct.util import html
from dynct.modules.commons import base
from dynct.modules.users import decorator as user_dec
from . import model

__author__ = 'justusadam'

ADMIN_PATH = '/admin'


@mvc.controller_function('admin', '', method=dchttp.RequestMethods.GET, query=False)
@user_dec.authorize('access admin pages')
@comp_dec.Regions
def overview(modelmap):

    modelmap.pageclasses = {'admin-menu', 'overview', 'admin-page'}
    modelmap['title'] = 'Website Administration'
    modelmap.theme = 'admin_theme'

    tree = order_tree(model.Category.select(),
                  [Category(child.machine_name, child.display_name, child.category, None) for child in
                model.Subcategory.select()])

    modelmap['content'] = render_categories(*tree)


def render_categories(*subcategories, basepath=ADMIN_PATH, classes=set()):
    subcategories = [a.render(basepath) for a in subcategories]
    if len(subcategories) == 1:
        return html.ContainerElement(*subcategories, classes=classes)
    else:
        half = len(subcategories) // 2
        return html.ContainerElement(
            html.ContainerElement(*subcategories[:half], classes={'left-column'}),
            html.ContainerElement(*subcategories[half:], classes={'right-column'}),
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



class OverviewCommon(base.Commons):
    source_table = 'admin'

    def __init__(self, conf, render_args, show_title, client):
        super().__init__(conf=conf,
                         render_args=render_args,
                         show_title=show_title,
                         client=client)

    def get_content(self, name):
        subcategories = [a.render(ADMIN_PATH) for a in order_tree(model.Category.select(),
                  [Category(child.machine_name, child.display_name, child.category, None) for child in
                model.Subcategory.select()])]
        return subcategories

    @property
    def title(self):
        return html.ContainerElement(super().title, html_type='a', additional={'href': '/admin'})


@mvc.controller_function('admin', '/\w+/(\w+)$', method=dchttp.RequestMethods.GET, query=False)
@comp_dec.Regions
def category(modelmap, name):
    modelmap.pageclasses = {'admin-menu', 'category'}

    parents = model.Category.get(machine_name=name)

    children = [Category(child.machine_name, child.display_name, child.category, None) for child in
                model.Subcategory.select().where(model.Subcategory.category == name)]

    tree = order_tree(parents, children)

    modelmap['content'] = render_categories(*tree)

    return 'page'


@mvc.controller_function('admin', '/(\w+)$', method=dchttp.RequestMethods.GET, query=False)
@comp_dec.Regions
def subcategory(modelmap, name):
    modelmap.pageclasses = {'admin-menu', 'subcategory'}

    parents = [model.Subcategory.get(model.Subcategory.machine_name == name)]

    children = model.AdminPage.select().where(model.AdminPage.subcategory == parents[0])

    tree = order_tree(parents, children)

    modelmap['content'] = render_categories(*tree)

    return 'page'


class Category:
    classes = {'category'}

    def __init__(self, name, display_name, parent=None, sub=None):
        self.name = name
        self.display_name = display_name
        self.sub = sub
        self.parent = parent

    def render(self, url_base):
        path = url_base + '/' + self.name
        title = html.ContainerElement(
            self.display_name, html_type='a', additional={'href': path}, classes=self.classes
        )
        if not self.sub:
            return title
        else:
            l = [a.render(path) for a in self.sub]
            return html.ContainerElement(
                title,
                html.List(
                    *l
                )
            )