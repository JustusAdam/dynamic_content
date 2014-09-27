from urllib import parse

from core.base_handlers import PageContentHandler, RedirectMixIn
from core.modules import Modules
from framework.html_elements import FormElement, TableElement, Input, Label, ContainerElement
from framework.url_tools import UrlQuery
from . import database_operations
from core.database_operations import ContentTypes, DBOperationError


__author__ = 'justusadam'


class FieldBasedPageContentHandler(PageContentHandler):
  modifier = 'show'

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.modules = Modules()
    (self.page_title, self.content_type, self._theme) = self.get_page_information()
    self.fields = self.get_fields()

  def get_fields(self):
    db_result = database_operations.Pages().get_fields(self.content_type)

    fields = []

    for (field_name, machine_name, handler_module) in db_result:
      handler = self.get_field_handler(machine_name, handler_module)
      fields.append(handler)

    return fields

  def handle_single_field_post(self, field_handler):
    query_keys = field_handler.get_post_query_keys()
    if query_keys:
      vals = {}
      for key in query_keys:
        if key in self._url.post_query.keys():
          vals[key] = self._url.post_query[key]
      if vals:
        field_handler.process_post(UrlQuery(vals))

  def handle_single_field_get(self, field_handler):
    query_keys = field_handler.get_post_query_keys()
    if query_keys:
      vals = {}
      for key in query_keys:
        if key in self._url.get_query.keys():
          vals[key] = self._url.post_query[key]
      if vals:
        field_handler.process_get(UrlQuery(vals))

  def get_field_handler(self, name, module):
    return self.modules[module].field_handler(name, self._url.page_type, self._url.page_id, self.modifier)

  def concatenate_content(self, fields):
    content = self.field_content(fields)
    return ContainerElement(*content)

  def field_content(self, fields):
    content = []
    for field in fields:
      content.append(field.compiled.content)
    return content

  def process_content(self):
    return self.concatenate_content(self.fields)

  def get_page_information(self):
    ops = database_operations.Pages()
    (content_type, title) = ops.get_page_information(self._url.page_type, self._url.page_id)
    theme = ops.get_theme(content_type=content_type)
    return title, content_type, theme


class EditFieldBasedContentHandler(FieldBasedPageContentHandler, RedirectMixIn):
  modifier = 'edit'

  field_identifier_separator = '-'

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.user = '1'
    self._is_post = bool(self._url.post_query)

  @property
  def title_options(self):
    return [Label('Title', label_for='edit-title'),
            Input(element_id='edit-title', name='title', value=self.page_title, required=True)]

  def concatenate_content(self, fields):
    content = [self.title_options]
    content += self.field_content(fields)
    content.append(self.admin_options)
    table = TableElement(*content, classes={'edit', self.content_type, 'edit-form'})
    return FormElement(table, action=str(self._url))

  def field_content(self, fields):
    content = []
    for field in fields:
      identifier = self.make_field_identifier(field.machine_name)
      c_fragment = field.compiled
      c_fragment.content.classes.add(self.content_type)
      c_fragment.content.element_id = identifier
      content.append((Label(field.machine_name, label_for=identifier), str(c_fragment.content)))
    return content

  def make_field_identifier(self, name):
    return self.modifier + self.field_identifier_separator + name

  @property
  def admin_options(self):
    return Label('Published', label_for='toggle-published'), \
           Input(element_id='toggle-published', input_type='radio', value='1', name='publish')

  def process_fields(self, fields):
    for field in fields:
      field.process_post()

  def assign_inputs(self, fields):
    for field in fields:
      mapping = {}
      for key in field.get_post_query_keys():
        if not key in self._url.post_query:
          raise KeyError
        mapping[key] = [parse.unquote_plus(a) for a in self._url.post_query[key]]
      field.query = mapping
  #
  # def alter_page(self):
  #   if not 'title' in self._url.post_query.keys():
  #     raise ValueError
  #   if self._url.post_query['title'] != self.page_title:
  #     self.page_title = parse.unquote_plus(self._url.post_query['title'][0])
  #   if 'publish' in self._url.post_query.keys():
  #     published = True
  #   else:
  #     published = False
  #   database_operations.Pages().edit_page(self._url.page_type, self.page_title, published, self._url.page_id)


class AddFieldBasedContentHandler(EditFieldBasedContentHandler):
  modifier = 'add'

  def get_page_information(self):
    ops = database_operations.Pages()
    if not 'ct' in self._url.get_query:
      raise ValueError
    content_type = self._url.get_query['ct'][0]
    display_name = ContentTypes().get_ct_display_name(content_type)
    title = 'Add new ' + display_name + ' page'
    theme = ops.get_theme(content_type=content_type)
    return title, content_type, theme
  #
  # def create_page(self):
  #   self.page_title = parse.unquote_plus(self._url.post_query['title'][0])
  #   if 'publish' in self._url.post_query.keys():
  #     published = True
  #   else:
  #     published = False
  #   return database_operations.Pages().add_page(self._url.page_type, self.content_type,
  #                                               self.page_title, self.user, published)

  @property
  def title_options(self):
    return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


