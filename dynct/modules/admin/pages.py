import collections

from dynct.core.mvc import content_compiler as _cc
from dynct.core.mvc import decorator as mvc_dec
from dynct.modules.comp import decorator as comp_dec
from dynct.modules.comp import html
from dynct.modules.commons import base

from . import model

__author__ = 'justusadam'

ADMIN_PATH = '/admin'



@mvc_dec.controller_function('admin', '', get=False, post=False)
@comp_dec.Regions
def overview(model):
    return OverviewPage(model, None).compile()


@mvc_dec.controller_function('admin', '/(\w+)$', get=False, post=False)
@comp_dec.Regions
def category(model, category):
    return CategoryPage(model, category).compile()


@mvc_dec.controller_function('admin', '/\w+/(\w+)$', get=False, post=False)
@comp_dec.Regions
def subcategory(model, subcategory):
    return SubcategoryPage(model, subcategory).compile()

#
# @controller_class
# class AdminController:
#     @controller_method('admin')
#     @Regions
#     def handle(self, model, url, get, post):
#         url.post = post
#         if model.client.user == GUEST:
#             model['content'] = 'Not authorized.'
#             model['title'] = 'Not Authorized.'
#             return 'page'
#         tail = url.path[1:]
#         if not tail:
#             handler = OverviewPage
#         elif len(tail) == 1:
#             handler = CategoryPage
#         elif len(tail) == 2:
#             handler = SubcategoryPage
#         else:
#             page = ar.AdminPage.get(machine_name=tail[2])
#             handler = Modules[page.handler_module].admin_handler(tail[2])
#         return handler(model, url).compile()


class Overview(_cc.ContentCompiler):
    classes = {'admin-menu', 'overview'}

    def __init__(self):
        self.page_title = 'Website Administration'

    def get_children_data(self):
        return model.Subcategory.select()

    def get_parents_data(self):
        return model.Category.select()

    def base_path(self):
        return ADMIN_PATH

    def render_categories(self, *subcategories):
        subcategories = [a.render(self.base_path()) for a in subcategories]
        if len(subcategories) == 1:
            return html.ContainerElement(*subcategories, classes=self.classes)
        else:
            half = len(subcategories) // 2
            return html.ContainerElement(
                html.ContainerElement(*subcategories[:half], classes={'left-column'}),
                html.ContainerElement(*subcategories[half:], classes={'right-column'}),
                classes=self.classes
            )

    def element_tree(self):
        return self.order_tree(self.get_parents_data(), self.get_children(Category))

    def order_tree(self, parents, children):
        mapping = collections.defaultdict(list)
        for item in children:
            mapping[item.parent].append(item)
        return [Category(name=parent.machine_name,
                         display_name=parent.display_name,
                         sub=mapping.get(parent.machine_name, None))
                for parent in parents]

    def get_children(self, child_class):
        return [child_class(child.machine_name, child.display_name, child.category, None) for child in
                self.get_children_data()]


class OverviewPage(_cc.Content, Overview):
    permission = 'access admin pages'
    theme = 'admin_theme'

    def __init__(self, model, url):
        super().__init__(model)
        Overview.__init__(self)
        self.classes = {'admin-menu', 'overview', 'admin-page'}
        self.url = url

    def process_content(self):
        return self.render_categories(*self.element_tree())


class OverviewCommon(base.Commons, Overview):
    source_table = 'admin'

    def __init__(self, conf, render_args, show_title, client):
        super().__init__(conf=conf,
                         render_args=render_args,
                         show_title=show_title,
                         client=client)
        Overview.__init__(self)

    def get_content(self, name):
        subcategories = [a.render(self.base_path()) for a in self.element_tree()]
        return subcategories

    @property
    def title(self):
        return html.ContainerElement(super().title, html_type='a', additional={'href': '/admin'})


class CategoryPage(OverviewPage):
    classes = {'admin-menu', 'category'}

    def __init__(self, model, url):
        super().__init__(model, url)
        if isinstance(url, str):
            self.name = url
        else:
            self.name = url.path[1]
        self.page_title = self.name

    def base_path(self):
        return '/admin'

    def get_parents_data(self):
        return [model.Category.get(model.Subcategory.machine_name==self.name)]

    def get_children_data(self):
        return model.Subcategory.select().where(model.Subcategory.category == self.name)


class SubcategoryPage(CategoryPage):
    classes = {'admin-menu', 'subcategory'}

    def __init__(self, model, url):
        super().__init__(model, url)
        if isinstance(url, str):
            self.name = url
        else:
            self.name = self.url.path[2]
        self.page_title = self.name

    def get_parents_data(self):
        return [model.Subcategory.get(model.Subcategory.machine_name == self.name)]

    def get_children_data(self):
        return model.AdminPage.select().where(model.AdminPage.subcategory == self.get_parents_data()[0])


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