from dynct.core.mvc.content_compiler import Content
from dynct.core.mvc.controller import Controller
from dynct.core.mvc.model import Model
from dynct.core.mvc.content_compiler import ContentCompiler
from dynct.core import Modules
from dynct.modules.comp.html_elements import ContainerElement, List
from dynct.modules.users.users import GUEST
from dynct.modules.users.client import ClientInfoImpl
from dynct.modules.commons.commons import Commons
from . import ar

__author__ = 'justusadam'

ADMIN_PATH = '/admin'


class AdminController(Controller):
    def __init__(self):
        super().__init__()
        self['admin'] = self.handle

    def handle(self, model, url, client:ClientInfoImpl):
        if client.user == GUEST:
            return Model('page', content='Not authorized.', title='Not Authorized.')
        tail = url.path[1:]
        if not tail:
            handler = OverviewPage
        elif len(tail) == 1:
            handler = CategoryPage
        elif len(tail) == 2:
            handler = SubcategoryPage
        else:
            page = ar.AdminPage.get(machine_name=tail[2])
            handler = Modules[page.handler_module].admin_handler(tail[2])
        return handler(url, client).compile()


class Overview(ContentCompiler):
    classes = {'admin-menu', 'overview'}

    def __init__(self):
        # self.ops = AdminOperations()
        self.page_title = 'Website Administration'

    def get_children_data(self):
        return ar.Subcategory.get_all()

    def get_parents_data(self):
        return ar.Category.get_all()

    def base_path(self):
        return ADMIN_PATH

    def render_categories(self, *subcategories):
        subcategories = [a.render(self.base_path()) for a in subcategories]
        if len(subcategories) == 1:
            return ContainerElement(*subcategories, classes=self.classes)
        else:
            half = len(subcategories) // 2
            return ContainerElement(
                ContainerElement(*subcategories[:half], classes={'left-column'}),
                ContainerElement(*subcategories[half:], classes={'right-column'}),
                classes=self.classes
            )

    def element_tree(self):
        return self.order_tree(self.get_parents_data(), self.get_children(Category))

    def order_tree(self, parents, children):
        mapping = {}
        for item in children:
            if item.parent in mapping:
                mapping[item.parent].append(item)
            else:
                mapping[item.parent] = [item]
        return [Category(parent.machine_name, parent.display_name, None, mapping.get(parent.machine_name, None)) for
                parent in parents]

    def get_children(self, child_class):
        return [child_class(child.machine_name, child.display_name, child.category, None) for child in
                self.get_children_data()]


class OverviewPage(Content, Overview):
    permission = 'access admin pages'
    theme = 'admin_theme'

    def __init__(self, model):
        super().__init__(None)
        Overview.__init__(self)
        self.classes = {'admin-menu', 'overview', 'admin-page'}
        self.url = url

    def process_content(self):
        return self.render_categories(*self.element_tree())


class OverviewCommon(Commons, Overview):
    source_table = 'admin'

    def __init__(self, conf, client):
        super().__init__(conf, client)
        Overview.__init__(self)

    def get_content(self, name):
        subcategories = [a.render(self.base_path()) for a in self.element_tree()]
        return subcategories

    @property
    def title(self):
        return ContainerElement(super().title, html_type='a', additional={'href': '/admin'})


class CategoryPage(OverviewPage):
    classes = {'admin-menu', 'category'}

    def __init__(self, model):
        super().__init__(None)
        self.name = url.path[1]
        self.page_title = self.name

    def base_path(self):
        return self.url.path.prt_to_str(0, -1)

    def get_parents_data(self):
        return [ar.Category.get(machine_name=self.name)]

    def get_children_data(self):
        return ar.Subcategory.get_all(category=self.name)


class SubcategoryPage(CategoryPage):
    classes = {'admin-menu', 'subcategory'}

    def __init__(self, model):
        super().__init__(None)
        self.name = self.url.path[2]
        self.page_title = self.name

    def get_parents_data(self):
        return [ar.Subcategory.get(machine_name=self.name)]

    def get_children_data(self):
        return ar.AdminPage.get_all(subcategory=self.name)


class Category:
    classes = {'category'}

    def __init__(self, name, display_name, parent, sub):
        self.name = name
        self.display_name = display_name
        self.sub = sub
        self.parent = parent

    def render(self, url_base):
        path = url_base + '/' + self.name
        title = ContainerElement(
            self.display_name, html_type='a', additional={'href': path}, classes=self.classes
        )
        if not self.sub:
            return title
        else:
            l = [a.render(path) for a in self.sub]
            return ContainerElement(
                title,
                List(
                    *l
                )
            )