"""
This file implements the basis for important default handler types.

It used to describe more functionality but has been refactored to be simpler and cleaner.

What remains are base classes that may be altered in the future but currently only serve as a launching point.

Eventually basic functions that the core demands these classes to implement may be added as empty functions
"""
from http import cookies
from pathlib import Path
import sys
from urllib.error import HTTPError

from core import Modules
from core.comp.template import Template
from framework.config_tools import read_config
from framework.html_elements import ContainerElement
from framework.page import Component
from framework.url_tools import Url


__author__ = 'justusadam'


class ContentHandler:
  @property
  def compiled(self):
    return ''

  def __str__(self):
    return str(self.compiled)


class ObjectHandler(ContentHandler):
  def __init__(self, url):
    super().__init__()
    assert isinstance(url, Url)
    self._url = url
    self._headers = set()
    self._cookies = None

  @property
  def client_info(self):
    return None

  def add_header(self, key, value):
    assert isinstance(key, str)
    assert isinstance(value, str)
    self._headers.add((key, value))

  def add_morsels(self, cookie):
    if not self._cookies:
      self._cookies = cookies.SimpleCookie()
    assert isinstance(cookie, (str, dict))
    self._cookies.load(cookie)

  @property
  def cookies(self):
    if not self._cookies:
      self._cookies = cookies.SimpleCookie()
    return self._cookies

  @property
  def headers(self):
    if self._cookies:
      # since rendering cookie values with the cookie object returns a string we split it again
      # to get header and value
      name, value = self._cookies.output().split(':', 1)
      # and remove redundant space at the beginning of the value string
      value = value[1:]
      self.add_header(name, value)
    return self._headers


class PageHandler(ObjectHandler):
  def __init__(self, url, client_info):
    super().__init__(url)
    self._client_info = client_info
    self.page_type = None
    self.content_type = 'text/html'
    self.encoding = sys.getfilesystemencoding()

  @property
  def encoded(self):
    return str(self.compiled).encode(self.encoding)

  @property
  def client_info(self):
    return self._client_info


class FieldHandler(ContentHandler):
  pass


class TemplateBasedContentHandler(ContentHandler):
  _theme = 'default_theme'

  template_name = None

  def __init__(self):
    super().__init__()
    self.theme_config = read_config(self.theme_path + '/config.json')
    self._template = Template(self.get_template_path())

  def get_template_path(self):
    path = self.theme_path
    if 'template_directory' in self.theme_config:
      path += '/' + self.theme_config['template_directory']
    else:
      path += '/' + 'templates'
    return path + '/' + self.template_name + '.html'

  def get_my_folder(self):
    return str(Path(sys.modules[self.__class__.__module__].__file__).parent)

  def get_config_folder(self):
    return self.get_my_folder()

  @property
  def theme(self):
    return self._theme

  @property
  def theme_path(self):
    return 'themes/' + self.theme

  @property
  def compiled(self):
    self.fill_template()
    page = Component(str(self._template))
    return page

  def fill_template(self):
    pass


class TemplateBasedPageHandler(PageHandler, TemplateBasedContentHandler):
  template_name = 'page'


class PageContentHandler(ObjectHandler, TemplateBasedContentHandler):
  theme = 'default_theme'

  template_name = 'content'

  page_title = 'Dynamic Page'

  def __init__(self, url, parent_handler):
    super().__init__(url)
    TemplateBasedContentHandler.__init__(self)
    self._parent = parent_handler

  @property
  def client_info(self):
    return self._parent.client_info

  def process_queries(self):
    if self.has_url_query():
      self.process_url_query()
    if self.is_post():
      self.process_post_query()

  def process_content(self):
    pass

  def has_url_query(self):
    return bool(self._url.get_query)

  def is_post(self):
    return self._url.is_post

  def process_url_query(self):
    pass

  def process_post_query(self):
    pass

  def fill_template(self):
    self.process_queries()
    self._template['content'] = self.process_content()
    self._template['title'] = self.page_title

  @property
  def compiled(self):
    self.fill_template()
    page = Component(str(self._template), title=self.page_title)
    return page


class RedirectMixIn(ObjectHandler):
  def redirect(self, destination=None):
    if 'destination' in self._url.get_query:
      destination = self._url.get_query['destination'][0]
    elif not destination:
      destination = str(self._url.path.prt_to_str(0, -1))
    raise HTTPError(str(self._url), 302, 'Redirect',
                    [('Location', destination), ('Connection', 'close'), ('Content-Type', 'text/html')], None)


class CommonsHandler:
  # used to identify items with internationalization
  com_type = 'commons'

  source_table = 'commons_config'

  dn_ops = None

  # temporary
  language = 'english'

  def __init__(self, machine_name, show_title, user, access_group):
    self.access_group = access_group
    self.user = user
    self.name = machine_name
    self.show_title = show_title

  def get_display_name(self, item, language='english'):
    if not self.dn_ops:
      self.dn_ops = Modules()['internationalization'].Operations()
    return self.dn_ops.get_display_name(item, self.source_table, language)

  def wrap_content(self, content):
    if self.show_title:
      title = ContainerElement(self.get_display_name(self.name), html_type='h3')
    else:
      title = ''
    if isinstance(content, (list, tuple, set)):
      return ContainerElement(title, *content, classes={self.name.replace('_', '-'), 'common'})
    else:
      return ContainerElement(title, content, classes={self.name.replace('_', '-'), 'common'})

  def get_content(self, name):
    return ''

  @property
  def compiled(self):
    obj = Component(self.wrap_content(self.get_content(self.name)))
    return obj