from core import handlers
from modules.admin.database_operations import AdminOperations
from modules.comp.html_elements import ContainerElement, List

__author__ = 'justusadam'

ADMIN_PATH = '/admin'


class Overview(handlers.base.AbstractContentCompiler):
    classes = {'admin-menu', 'overview'}

    def __init__(self):
        self.ops = AdminOperations()
        self.page_title = 'Website Administration'

    def get_children_data(self):
        return self.ops.get_subcategories()

    def get_parents_data(self):
        return self.ops.get_categories()

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
        return [Category(machine_name, display_name, None, mapping.get(machine_name, None)) for
                (machine_name, display_name) in parents]

    def get_children(self, child_class):
        return [child_class(machine_name, display_name, category, None) for (machine_name, display_name, category) in
                self.get_children_data()]


class OverviewPage(handlers.content.Content, Overview):
    permission = 'access admin pages'

    def __init__(self, request, client):
        super().__init__(request, client)
        Overview.__init__(self)
        self.classes = {'admin-menu', 'overview', 'admin-page'}

    def process_content(self):
        return self.render_categories(*self.element_tree())


class OverviewCommon(handlers.common.Commons, Overview):
    source_table = 'admin'

    def __init__(self, machine_name, show_title, access_type, client):
        super().__init__(machine_name, show_title, access_type, client)
        Overview.__init__(self)

    def get_content(self, name):
        subcategories = [a.render(self.base_path()) for a in self.element_tree()]
        return subcategories

    @property
    def title(self):
        return ContainerElement(super().title, html_type='a', additionals={'href': '/admin'})


class CategoryPage(OverviewPage):
    classes = {'admin-menu', 'category'}

    def base_path(self):
        return self.request.path.prt_to_str(0, -1)

    def get_parents_data(self):
        return self.ops.get_categories(self.request.tail[0])

    def get_children_data(self):
        return self.ops.get_subcategories(self.request.tail[0])


class SubcategoryPage(CategoryPage):
    classes = {'admin-menu', 'subcategory'}

    def __init__(self, request, client):
        super().__init__(request, client)
        self.name = self.request.tail[1]

    def get_parents_data(self):
        return self.ops.get_subcategories_info(self.name)

    def get_children_data(self):
        return self.ops.get_cat_pages(self.name)


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
            self.display_name, html_type='a', additionals={'href': path}, classes=self.classes
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