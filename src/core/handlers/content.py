from core.handlers.base import WebObject, TemplateBasedContentCompiler
from errors import html_message
from modules.comp.html_elements import List, ContainerElement
from modules.comp.page import Component

__author__ = 'justusadam'


class Content(WebObject, TemplateBasedContentCompiler):

  theme = 'default_theme'
  template_name = 'content'
  page_title = 'Dynamic Page'
  permission = 'access pages'
  published = True
  permission_for_unpublished = 'access unpublished pages'

  def __init__(self, url, parent_handler):
    super().__init__(url)
    TemplateBasedContentCompiler.__init__(self)
    self._parent = parent_handler

  @property
  def client(self):
    return self._parent.client

  def process_content(self):
    pass

  def editorial(self):
    l = self.editorial_list()
    if l:
      return List(
        *[ContainerElement(name, html_type='a', classes={'editorial-link'}, additionals={'href': link}) for name,link in l],
        classes={'editorial-list'}
      )
    return ''

  def editorial_list(self):
    return []

  def has_url_query(self):
    return bool(self._url.get_query)

  def _fill_template(self):
    self._template['editorial'] = self.editorial()
    self._template['content'] = self.process_content()
    self._template['title'] = self.page_title

  def check_own_permission(self):
    if not self.published:
      if not self.check_permission(self.permission_for_unpublished):
        return False
    return self.check_permission(self.permission)

  def check_permission(self, permission):
    return self.client.check_permission(permission)

  @property
  def compiled(self):
    if self.check_own_permission():
      self._process_queries()
      self._fill_template()
      page = Component(str(self._template), title=self.page_title)
      return page
    else:
      return Component(str(html_message.error_message(401)))