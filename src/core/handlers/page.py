import sys
from core.handlers.base import WebObject, TemplateBasedContentCompiler

__author__ = 'justusadam'


class Page(WebObject):
  def __init__(self, data_shell, url, client):
    super().__init__(data_shell, url)
    self._client = client
    self.page_type = None
    self.content_type = 'text/html'
    self.encoding = sys.getfilesystemencoding()

  @property
  def encoded(self):
    return str(self.compiled).encode(self.encoding)

  @property
  def client(self):
    return self._client


class TemplateBasedPage(Page, TemplateBasedContentCompiler):
  template_name = 'page'