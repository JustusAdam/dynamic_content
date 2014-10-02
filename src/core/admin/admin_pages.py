from core.handlers import PageContent
from .database_operations import AdminOperations
from framework.html_elements import ContainerElement, List

__author__ = 'justusadam'


class Overview(PageContent):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.ops = AdminOperations()
    self.page_title = 'Website Administration'

  def process_content(self):
    return self.render_categories(*self.element_tree())

  def get_children_data(self):
    return self.ops.get_subcategories()

  def get_parents_data(self):
    return self.ops.get_categories()

  def base_path(self):
    return '/admin'

  def render_categories(self, *subcategories):
    subcategories = [a.render(self.base_path()) for a in subcategories]
    if len(subcategories) == 1:
      return ContainerElement(*subcategories)
    else:
      half = len(subcategories) // 2
      return ContainerElement(
        ContainerElement(*subcategories[:half]),
        ContainerElement(*subcategories[half:])
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
    return [Category(machine_name, display_name, None, mapping.get(machine_name, None)) for (machine_name, display_name) in parents]

  def get_children(self, child_class):
    return [child_class(machine_name, display_name, category, None) for (machine_name, display_name, category) in self.get_children_data()]


class CategoryPage(Overview):

  def base_path(self):
    return self.url.path.prt_to_str(0, -1)

  def get_parents_data(self):
    return self.ops.get_categories(self.url.tail[0])

  def get_children_data(self):
    return self.ops.get_subcategories(self.url.tail[0])


class SubcategoryPage(CategoryPage):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.name = self.url.tail[1]

  def get_parents_data(self):
    return self.ops.get_subcategories_info(self.name)

  def get_children_data(self):
    return self.ops.get_cat_pages(self.name)


class Category:

  def __init__(self, name, display_name, parent, sub):
    self.name = name
    self.display_name = display_name
    self.sub = sub
    self.parent = parent

  def render(self, url_base):
    path = url_base + '/' + self.name
    title = ContainerElement(
        self.display_name, html_type='a', additionals={'href': path}
      )
    if not self.sub:
      return title
    else:
      list = [a.render(path) for a in self.sub]
      return ContainerElement(
        title,
        List(
          *list
        )
      )