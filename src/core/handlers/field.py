from core.handlers.base import Content
from framework.html_elements import ContainerElement
from framework.page import Component

__author__ = 'justusadam'


class Field(Content):
  _query = {}
  db_ops = None

  def __init__(self, path_prefix, page_id, machine_name):
    super().__init__()
    self.page_id = page_id
    self.machine_name = machine_name
    self.path_prefix = path_prefix

  @property
  def query(self):
    return {}

  @query.setter
  def query(self, value):
    self._query = value

  @property
  def compiled(self):
    content = ContainerElement(self.process_content(), element_id='field-' + self.machine_name, classes={'field'})
    if not content:
      return False
    return Component(content)

  def get_field_title(self):
    return self.machine_name

  def process_content(self):
    return self.get_content()

  @property
  def post_query_keys(self):
    return []

  def process_post(self):
    pass

  def get_content(self):
    if not self.page_id:
      return ''

    return self.db_ops.get_content(self.machine_name, self.path_prefix, self.page_id)