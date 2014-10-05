from core.errors import html_message
from core.handlers.base import WebObject, TemplateBasedContent
from framework.page import Component

__author__ = 'justusadam'


class Content(WebObject, TemplateBasedContent):

  theme = 'default_theme'
  template_name = 'content'
  page_title = 'Dynamic Page'
  permission = 'access pages'

  def __init__(self, url, parent_handler):
    super().__init__(url)
    TemplateBasedContent.__init__(self)
    self._parent = parent_handler

  @property
  def client(self):
    return self._parent.client

  def process_content(self):
    pass

  def has_url_query(self):
    return bool(self._url.get_query)

  def fill_template(self):
    self._template['content'] = self.process_content()
    self._template['title'] = self.page_title

  def check_permission(self):
    return self.client.check_permission(self.permission)

  @property
  def compiled(self):
    if self.check_permission():
      self.process_queries()
      self.fill_template()
      page = Component(str(self._template), title=self.page_title)
      return page
    else:
      return Component(str(html_message.error_message(401)))