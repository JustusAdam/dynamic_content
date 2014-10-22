from urllib import parse

from core import handlers
from core.modules import Modules
from modules.comp.html_elements import FormElement, TableElement, Input, Label, ContainerElement, Checkbox
from util.url import UrlQuery
from . import database_operations
from core.database_operations import ContentTypes


__author__ = 'justusadam'

_access_modifier = 'access'
_edit_modifier = 'edit'
_add_modifier = 'add'


class FieldBasedPageContent(handlers.content.Content):
    modifier = _access_modifier
    _editorial_list_base = edits = [('edit', _edit_modifier)]

    def __init__(self, request, client):
        super().__init__(request, client)
        self.modules = Modules()
        (self.page_title, self.content_type, self._theme, self.published) = self.get_page_information()
        self.fields = self.get_fields()
        self.permission = self.join_permission(self.modifier, self.content_type)
        self.permission_for_unpublished = self.join_permission('access unpublished', self.content_type)

    def join_permission(self, modifier, content_type):
        return ' '.join([modifier, 'content type', content_type])

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
                if key in self.request.post:
                    vals[key] = self.request.post[key]
            if vals:
                field_handler.process_post(UrlQuery(vals))

    def handle_single_field_get(self, field_handler):
        query_keys = field_handler.get_post_query_keys()
        if query_keys:
            vals = {}
            for key in query_keys:
                if key in self.request.get_query:
                    vals[key] = self.request.post[key]
            if vals:
                field_handler.process_get(UrlQuery(vals))

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self.request.page_type, self.request.page_id, self.modifier)

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
        (content_type, title, published) = ops.get_page_information(self.request.page_type, self.request.page_id)
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme, published

    def editorial_list(self):
        s = []
        for (name, modifier) in self._editorial_list_base:
            if self.check_permission(self.join_permission(modifier, self.content_type)):
                s.append((name, '/'.join(['', self.request.page_type, str(self.request.page_id), modifier])))
        return s


class EditFieldBasedContent(FieldBasedPageContent, handlers.base.RedirectMixIn):
    modifier = _edit_modifier
    _editorial_list_base = [('show', _access_modifier)]
    field_identifier_separator = '-'

    def __init__(self, request, client):
        super().__init__(request, client)
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
        return FormElement(table, action=str(self.request))

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
               Checkbox(element_id='toggle-published', value='published', name='published',
                     checked=self.published)

    def process_fields(self, fields):
        for field in fields:
            field.process_post()

    def assign_inputs(self, fields):
        for field in fields:
            mapping = {}
            for key in field.post_query_keys:
                if not key in self.request.post:
                    raise KeyError
                mapping[key] = [parse.unquote_plus(a) for a in self.request.post[key]]
            field.query = mapping

    def process_page(self):
        if not 'title' in self.request.post:
            raise ValueError
        if self.request.post['title'] != self.page_title:
            self.page_title = parse.unquote_plus(self.request.post['title'][0])
        if 'publish' in self.request.post:
            published = True
        else:
            published = False
        database_operations.Pages().edit_page(self.request.page_type, self.page_title, published, self.request.page_id)

    def _process_query(self):
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
        if not 'ct' in self.request.get_query:
            raise ValueError
        content_type = self.request.get_query['ct'][0]
        display_name = ContentTypes().get_ct_display_name(content_type)
        title = 'Add new ' + display_name + ' page'
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme, True

    def process_page(self):
        self.page_title = parse.unquote_plus(self.request.post['title'][0])
        if 'publish' in self.request.post:
            published = True
        else:
            published = False
        page_id = database_operations.Pages().add_page(self.request.page_type, self.content_type,
                                                       self.page_title, self.user, published)
        self.update_field_page_id(page_id)
        self.request.page_id = page_id
        return self.request.path.prt_to_str(0, -1) + '/' + str(self.request.page_id)


    def update_field_page_id(self, page_id):
        for field in self.fields:
            field.page_id = page_id

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


