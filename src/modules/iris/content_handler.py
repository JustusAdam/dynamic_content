from urllib import parse

from core import handlers
from core.modules import Modules
from modules.comp.html_elements import FormElement, TableElement, Input, Label, ContainerElement
from util.url import UrlQuery
from . import database_operations
from core.database_operations import ContentTypes


__author__ = 'justusadam'


class FieldBasedPageContent(handlers.content.Content):
  modifier = 'access'

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.modules = Modules()
    (self.page_title, self.content_type, self._theme) = self.get_page_information()
    self.fields = self.get_fields()
    self.permission = ' '.join([self.modifier, 'content type', self.content_type])

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
        if key in self.url.post:
          vals[key] = self.url.post[key]
      if vals:
        field_handler.process_post(UrlQuery(vals))

  def handle_single_field_get(self, field_handler):
    query_keys = field_handler.get_post_query_keys()
    if query_keys:
      vals = {}
      for key in query_keys:
        if key in self.url.get_query:
          vals[key] = self.url.post[key]
      if vals:
        field_handler.process_get(UrlQuery(vals))

  def get_field_handler(self, name, module):
    return self.modules[module].field_handler(name, self.url.page_type, self.url.page_id, self.modifier)

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
    (content_type, title) = ops.get_page_information(self.url.page_type, self.url.page_id)
    theme = ops.get_theme(content_type=content_type)
    return title, content_type, theme


class EditFieldBasedContent(FieldBasedPageContent, handlers.base.RedirectMixIn):
  modifier = 'edit'

  field_identifier_separator = '-'

  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.user = '1'

  @property
  def title_options(self):
    return [Label('Title', label_for='edit-title'),
            Input(element_id='edit-title', name='title', value=self.page_title, required=True)]

  def concatenate_content(self, fields):
    content = [self.title_options]
    content += self.field_content(fields)
    content.append(self.admin_options)
    table = TableElement(*content, classes={'edit', self.content_type, 'edit-form'})
    return FormElement(table, action=str(self.url))

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
      for key in field.post_query_keys:
        if not key in self.url.post:
          raise KeyError
        mapping[key] = [parse.unquote_plus(a) for a in self.url.post[key]]
      field.query = mapping
  
  def process_page(self):
    if not 'title' in self.url.post:
      raise ValueError
    if self.url.post['title'] != self.page_title:
      self.page_title = parse.unquote_plus(self.url.post['title'][0])
    if 'publish' in self.url.post:
      published = True
    else:
      published = False
    database_operations.Pages().edit_page(self.url.page_type, self.page_title, published, self.url.page_id)

  def _process_post(self):
    self.assign_inputs(self.fields)
    try:
      page = self.process_page()
      self.process_fields(self.fields)
      self.redirect(page)
    except ValueError:
      pass


class AddFieldBasedContentHandler(EditFieldBasedContent):
  modifier = 'add'

  def get_page_information(self):
    ops = database_operations.Pages()
    if not 'ct' in self.url.get_query:
      raise ValueError
    content_type = self.url.get_query['ct'][0]
    display_name = ContentTypes().get_ct_display_name(content_type)
    title = 'Add new ' + display_name + ' page'
    theme = ops.get_theme(content_type=content_type)
    return title, content_type, theme
  
  def process_page(self):
    self.page_title = parse.unquote_plus(self.url.post['title'][0])
    if 'publish' in self.url.post:
      published = True
    else:
      published = False
    page_id = database_operations.Pages().add_page(self.url.page_type, self.content_type,
                                                self.page_title, self.user, published)
    self.update_field_page_id(page_id)
    self.url.page_id = page_id
    return self.url.path.prt_to_str(0,-1) + '/' + str(self.url.page_id)


  def update_field_page_id(self, page_id):
    for field in self.fields:
      field.page_id = page_id

  @property
  def title_options(self):
    return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


