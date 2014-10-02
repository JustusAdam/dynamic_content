from core.handlers import PageContent
from .database_operations import AdminOperations
from framework.html_elements import ContainerElement, List

__author__ = 'justusadam'


class Overview(PageContent):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.ops = AdminOperations()

  def process_content(self):
    return self.render_categories(*self.element_tree())

  def get_children(self):
    return self.ops.get_subcategories()

  def get_parents(self):
    return self.ops.get_categories()

  def render_categories(self, *subcategories):
    subcategories = [a.render(str(self.url.path)) for a in subcategories]
    if len(subcategories) == 1:
      return ContainerElement(*subcategories)
    else:
      half = len(subcategories) // 2
      return ContainerElement(
        ContainerElement(*subcategories[:half]),
        ContainerElement(*subcategories[half:])
      )

  def element_tree(self):
    return self.order_tree(self.get_parents(), self.subcategories())

  def order_tree(self, parents, children):
    mapping = {}
    for item in children:
      if item.name in mapping:
        mapping[item.name].append(item)
      else:
        mapping[item.name] = [item]
    return [Category(machine_name, display_name, None, mapping.get(machine_name, None)) for (machine_name, display_name) in parents]

  def subcategories(self):
    return [Category(machine_name, display_name, category, None) for (machine_name, display_name, category) in self.get_children()]


class CategoryPage(Overview):

  def get_parents(self):
    return self.ops.get_categories(self.url.tail[0])

  def get_children(self):
    return self.ops.get_subcategories(self.url.tail[0])


class SubcategoryPage(Overview):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.name = self.url.tail[1]

  def get_parents(self):
    return self.ops.get_subcategories(self.name)

  def get_children(self):
    return self.ops.get_cat_pages(self.name)


class Category:

  def __init__(self, name, display_name, parent, sub):
    self.name = name
    self.display_name = display_name
    self.sub = sub

  def render(self, url_base):
    path = url_base + '/' + self.name
    title = ContainerElement(
        self.display_name, html_type='a', additionals={'href': path}
      )
    if not self.sub:
      return title
    else:
      return ContainerElement(
        title,
        List(
          [a.render(path) for a in self.sub]
        )
      )