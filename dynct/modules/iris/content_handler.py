from urllib import parse

from dynct.core import handlers
from dynct.core.modules import Modules
from dynct.core.mvc.controller import Controller
from dynct.modules.comp.html_elements import FormElement, TableElement, Input, Label, ContainerElement, Checkbox
from dynct.util.url import UrlQuery
from . import database_operations
from dynct.core.database_operations import ContentTypes
from dynct.errors import InvalidInputError


__author__ = 'justusadam'

_access_modifier = 'access'
_edit_modifier = 'edit'
_add_modifier = 'add'


def wrap_compiler(class_):
    def wrapped(*args, **kwargs):
        return class_(*args, **kwargs).compiled
    return wrapped


class FieldBasedPageContent(handlers.content.Content):
    modifier = _access_modifier
    _editorial_list_base = edits = [('edit', _edit_modifier)]

    def __init__(self, url, client):
        super().__init__(url, client)
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
        (content_type, title, published) = ops.get_page_information(self.url.page_type, self.url.page_id)
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme, published

    def editorial_list(self):
        s = []
        for (name, modifier) in self._editorial_list_base:
            if self.check_permission(self.join_permission(modifier, self.content_type)):
                s.append((name, '/'.join(['', self.url.page_type, str(self.url.page_id), modifier])))
        return s


class EditFieldBasedContent(FieldBasedPageContent, handlers.base.RedirectMixIn):
    modifier = _edit_modifier
    _editorial_list_base = [('show', _access_modifier)]
    field_identifier_separator = '-'

    def __init__(self, url, client):
        super().__init__(url, client)
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
               Checkbox(element_id='toggle-published', value='published', name='published',
                     checked=self.published)

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
        return title, content_type, theme, True

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
        return self.url.path.prt_to_str(0, -1) + '/' + str(self.url.page_id)


    def update_field_page_id(self, page_id):
        for field in self.fields:
            field.page_id = page_id

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


class IrisController(Controller):
    handler_map = {
        _access_modifier: FieldBasedPageContent,
        _edit_modifier: EditFieldBasedContent,
        _add_modifier: AddFieldBasedContentHandler
    }

    def __init__(self):
        super().__init__(iris=self.handle)

    def handle(self, url, client):
        if len(url.path) == 3:
            if url.path[1].isdigit():
                raise InvalidInputError
            url.page_id = int(url.path[1])
            url.page_modifier = url.path[2]
        elif len(url.path) == 2:
            if url.path[1].isdigit():
                url.page_id = int(url.path[1])
                url.page_modifier = _access_modifier
            else:
                if not url.path[1] == _add_modifier:
                    raise InvalidInputError
                url.page_modifier = _add_modifier
        else:
            raise InvalidInputError
        url.page_type = url.path[0]
        return self.handler_map[url.page_modifier](url, client).compiled