from core.handlers import PageContent
from .database_operations import AdminOperations
from framework.html_elements import ContainerElement, List

__author__ = 'justusadam'


class Overview(PageContent):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.ops = AdminOperations()

  def process_content(self):
    return self.render_categories(self.categories())

  def get_subcategories(self):
    return self.ops.get_subcategories()

  def get_categories(self):
    return self.ops.get_categories()

  def render_categories(self, *subcategories):
    subcategories = [a.render() for a in subcategories]
    if len(subcategories) == 1:
      return ContainerElement(*subcategories)
    else:
      half = len(subcategories) / 2
      return ContainerElement(
        ContainerElement(*subcategories[:half]),
        ContainerElement(*subcategories[half:])
      )

  def categories(self):
    c = self.get_categories()
    e = self.subcategories()
    mapping = {}
    for item in e:
      if item.name in mapping:
        mapping[item.name].append(item)
      else:
        mapping[item.name] = [item]
    return [Category(machine_name, display_name, category, mapping[machine_name]) for (machine_name, display_name, category) in c]

  def subcategories(self):
    return [Category(machine_name, display_name, category, None) for (machine_name, display_name, category) in self.get_subcategories()]


class CategoryPage(Overview):

  def render_categories(self, *subcategories):
    pass

  def categories(self):
    return Category()


class Category:

  def __init__(self, name, display_name, parent, sub):
    self.name = name
    self.display_name = display_name
    self.sub = sub

  def render(self, url_base):
    title = ContainerElement(
        self.display_name, html_type='a', additionals={'href': url_base + '/' + self.name}
      )
    if not self.sub:
      return title
    else:
      return ContainerElement(
        title,
        List(
          [a.render() for a in self.sub]
        )
      )