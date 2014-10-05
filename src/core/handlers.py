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
from framework.url import Url


__author__ = 'justusadam'


class Content:
  @property
  def compiled(self):
    return ''

  def __str__(self):
    return str(self.compiled)


class WebObject(Content):

  _url = None

  def __init__(self, url):
    super().__init__()
    self.url = url
    self._headers = set()
    self._cookies = None

  @property
  def url(self):
    return self._url

  @url.setter
  def url(self, val):
    if not isinstance(val, Url):
      self._url = Url(val)
    else:
      self._url = val

  @property
  def client(self):
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

  def is_get(self):
    return bool(self.url.get_query)

  def is_post(self):
    return bool(self.url.post)

  def process_queries(self):
    """
    Simple routine that calls the appropriate 'process' methods IF they're necessary
    :return:
    """
    if self.is_get():
      self.process_get()
    if self.is_post():
      self.process_post()

  def process_get(self):
    """
    This method gets called by the class IF there are get query variables present.

    Inheriting classes should overwrite this method rather than 'process_queries'.
    :return:
    """
    pass

  def process_post(self):
    """
    This method gets called if there is a valid post query present.

    Inheriting classes should overwrite this method rather than 'process_queries'.
    :return:
    """
    pass


class Page(WebObject):
  def __init__(self, url, client):
    super().__init__(url)
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


class TemplateBasedContent(Content):
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


class TemplateBasedPage(Page, TemplateBasedContent):
  template_name = 'page'


class PageContent(WebObject, TemplateBasedContent):
  theme = 'default_theme'

  template_name = 'content'

  page_title = 'Dynamic Page'

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

  @property
  def compiled(self):
    self.process_queries()
    self.fill_template()
    page = Component(str(self._template), title=self.page_title)
    return page


class RedirectMixIn(WebObject):
  def redirect(self, destination=None):
    if 'destination' in self.url.get_query:
      destination = self.url.get_query['destination'][0]
    elif not destination:
      destination = str(self.url.path.prt_to_str(0, -1))
    raise HTTPError(str(self.url), 302, 'Redirect',
                    [('Location', destination), ('Connection', 'close'), ('Content-Type', 'text/html')], None)


class Commons:
  # used to identify items with internationalization
  com_type = 'commons'

  source_table = 'commons_config'

  dn_ops = None

  # temporary
  language = 'english'

  def __init__(self, machine_name, show_title, client):
    self.client = client
    self.name = machine_name
    self.show_title = show_title

  def get_display_name(self, item, language='english'):
    if not self.dn_ops:
      self.dn_ops = Modules()['internationalization'].Operations()
    return self.dn_ops.get_display_name(item, self.source_table, language)

  @property
  def title(self):
    return self.get_display_name(self.name)

  def wrap_content(self, content):
    if self.show_title:
      title = ContainerElement(self.title, html_type='h3')
    else:
      title = ''
    if isinstance(content, (list, tuple, set)):
      return ContainerElement(title, *content, classes={self.name.replace('_', '-'), 'common'})
    else:
      return ContainerElement(title, content, classes={self.name.replace('_', '-'), 'common'})

  def get_content(self, name):
    return ''

  def check_permission(self, permission):
    return self.client.check_permission(permission)

  def check_access(self):
    return self.check_permission('access common ' + self.name)

  @property
  def compiled(self):
    if self.check_access():
      obj = Component(self.wrap_content(self.get_content(self.name)))
      return obj
    else:
      return None