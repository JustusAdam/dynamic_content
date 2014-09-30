from core.handlers import PageContent
from .database_operations import AdminOperations

__author__ = 'justusadam'


class Overview(PageContent):

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)

  def process_content(self):
    pass

  def get_elements(self):
    ops = AdminOperations()
    pass