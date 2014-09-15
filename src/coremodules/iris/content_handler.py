from urllib import parse

from framework.base_handlers import ContentHandler
from core.modules import Modules
from framework.page import Page
from framework.html_elements import FormElement, TableElement, Input, Label
from framework.url_tools import UrlQuery
from . import database_operations


__author__ = 'justusadam'


class FieldBasedContentHandler(ContentHandler):

    modifier = 'show'

    def __init__(self, url):
        super().__init__(url)
        self.modules = Modules()
        (self.page_title, self.content_type, self.theme) = self.get_page_information()
        self.fields = self.get_fields()

    def get_page_information(self):
        ops = database_operations.ContentTypes()
        (content_type, title) = ops.get_page_information(self._url.page_type, self._url.page_id)
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme

    def get_fields(self):
        db_result = database_operations.ContentTypes().get_fields(self.content_type)

        fields = []

        for (field_name, machine_name, handler_module) in db_result:
            handler = self.get_field_handler(machine_name, handler_module)
            field = FieldInfo(field_name, machine_name, handler)
            fields.append(field)

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

    def handle_fields(self):
        for field in self.fields:
            field.value = field.handler.compiled
            self.integrate(field.value)
        return True

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self._url.page_type, self._url.page_id, self.modifier)

    def integrate(self, component):
        for stylesheet in component.stylesheets:
            self.page.stylesheets.add(stylesheet)
        for metatag in component.metatags:
            self.page.metatags.add(metatag)
        for script in component.scripts:
            self.page.scripts.add(script)

    def concatenate_content(self):
        content = ''
        for field in self.fields:
            content += str(field.value.content)
        return content

    @property
    def compiled(self):
        # executing step by step since any failing will fail all subsequent steps
        self.get_page_information()
        self.page = Page(self._url, self.page_title)
        if self.theme:
            self.page.used_theme = self.theme
        self.get_fields()
        self.handle_fields()
        self.page.content = self.concatenate_content()
        return self.page


class EditFieldBasedContentHandler(FieldBasedContentHandler):

    modifier = 'edit'

    def __init__(self, url):
        super().__init__(url)
        self.user = '1'
        self._is_post = bool(self._url.post_query)

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title',name='title', value=self.page_title, required=True)]

    def concatenate_content(self):
        content = [self.title_options]
        for field in self.fields:
            identifier = self.make_field_identifier(field)
            field.value.content.element_id = identifier
            content.append((Label(field.field_name, label_for=identifier), field.value.content))
        content.append(self.admin_options)
        table = TableElement(*content)
        if 'destination' in self._url.get_query:
            dest = '?destination=' + self._url.get_query['destination'][0]
        else:
            dest = ''
        return str(FormElement(table, action=str(self._url) + dest))

    def make_field_identifier(self, field):
        return self.modifier + '-' + field.value.title

    @property
    def admin_options(self):
        return Label('Published', label_for='toggle-published'), Input(element_id='toggle-published', input_type='radio', value='1', name='publish')

    def process_query(self):
        for field in self.fields:
            field.handler.process_post()

    def assign_inputs(self):
        for field in self.fields:
            mapping = {}
            for key in field.handler.get_post_query_keys():
                if not key in self._url.post_query:
                    print(key)
                    raise KeyError
                mapping[key] = [parse.unquote_plus(a) for a in self._url.post_query[key]]
            field.handler.query = mapping


    @property
    def compiled(self):
        self.get_page_information()
        self.page = Page(self._url, self.page_title)
        if self.theme:
            self.page.used_theme = self.theme
        self.get_fields()
        if self._is_post:
            self.process_post()
        self.handle_fields()
        self.page.content = self.concatenate_content()
        return self.page

    def process_post(self):
        self.assign_inputs()
        self.alter_page()
        self.process_query()

    def alter_page(self):
        if not 'title' in self._url.post_query.keys():
            raise ValueError
        if self._url.post_query['title'] != self.page_title:
            self.page_title = parse.unquote_plus(self._url.post_query['title'][0])
        if 'publish' in self._url.post_query.keys():
            published = True
        else:
            published = False
        database_operations.ContentTypes().edit_page(self._url.page_type, self.page_title, published)


class AddFieldBasedContentHandler(EditFieldBasedContentHandler):

    modifier = 'add'

    def __init__(self, url):
        super().__init__(url)

    def get_page_information(self):
        ops = database_operations.ContentTypes()
        if not 'ct' in self._url.get_query:
            raise ValueError
        content_type = self._url.get_query['ct']
        title = 'Add new ' + self._url.page_type + ' page'
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme

    def create_page(self):
        self.page_title = parse.unquote_plus(self._url.post_query['title'][0])
        if 'publish' in self._url.post_query.keys():
            published = True
        else:
            published = False
        return database_operations.ContentTypes().add_page(self._url.page_type, self.content_type, self.page_title, self.user, published)

    def process_post(self):
        self.assign_inputs()
        new_id = self.create_page()
        for field in self.fields:
            field.handler.page_id = new_id
        self.process_query()

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


class FieldInfo:

    def __init__(self, field_name, machine_name, handler=None):
        self.field_name = field_name
        self.machine_name = machine_name
        self.handler = handler
        self.value = None

