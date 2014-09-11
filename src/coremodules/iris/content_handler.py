from core.base_handlers import ContentHandler
from core.database import escape_item, Database
from core.modules import Modules
from core.page import Page
from framework.html_elements import FormElement, TableElement, Input, Label
from framework.url_tools import UrlQuery
from urllib import parse

__author__ = 'justusadam'


class FieldBasedContentHandler(ContentHandler):

    def __init__(self, url):
        super().__init__(url)
        self.field_values = []
        self.page_title = ''
        self.content_type = ''
        self.theme = ''
        self.field_handlers = []
        self.db = Database()
        self.modules = Modules({})


    def get_page_information(self):
        db_result = self.db.select(('content_type', 'page_title'), self._url.page_type, 'where id = ' + escape_item(self._url.page_id, 'utf-8')).fetchone()
        if not db_result:
            # TODO specify this exception
            raise Exception
        (self.content_type, self.page_title) = db_result
        db_result = self.db.select('theme', 'content_types', 'where content_type_name=' + escape_item(self.content_type, 'utf-8')).fetchone()
        if db_result:
            self.theme = db_result[0]
        return True

    def get_field_info(self):
        db_result = self.db.select(('field_name', 'handler_module', 'weight', 'machine_name'), 'page_fields', 'where content_type = ' + escape_item(self.content_type, 'utf-8')).fetchall()
        if db_result is None:
            # TODO specify this Exception
            raise Exception
        acc = sorted(db_result, key=lambda a: a[2])
        return acc

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

    def get_fields(self):
        field_info = self.get_field_info()
        for name in field_info:
            self.field_handlers.append(self.get_field_handler(name[0], name[1]))
        return True

    def handle_fields(self):
        for field in self.field_handlers:
            if not field.compile():
                return False
            field_value = field.field
            self.field_values.append(field_value)
            self.integrate(field_value)
        return True

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self.db, self._url.page_id)

    def integrate(self, component):
        for stylesheet in component.stylesheets:
            self._page.stylesheets.add(stylesheet)
        for metatag in component.metatags:
            self._page.metatags.add(metatag)
        for script in component.scripts:
            self._page.scripts.add(script)

    def concatenate_content(self):
        content = ''
        for field in self.field_values:
            content += str(field.content)
        return content

    def assign_content(self):
        self._page.content = self.concatenate_content()
        return True

    def compile(self):
        # executing step by step since any failing will fail all subsequent steps
        self.get_page_information()
        self._page = Page(self._url, self.page_title)
        if self.theme:
            self._page.used_theme = self.theme
        self.get_fields()
        self.handle_fields()
        self.assign_content()
        self._is_compiled = True
        return 200


class EditFieldBasedContentHandler(FieldBasedContentHandler):
    def __init__(self, url):
        super().__init__(url)
        self.user = '1'
        self._is_post = bool(self._url.post_query)
        self.modifier = 'edit'

    def get_field_handler(self, name, module):
        return self.modules[module].edit_field_handler(name, self.db, self._url.page_id)

    def title_input(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title',name='title', value=self.page_title, required=True)]

    def concatenate_content(self):
        content = [self.title_input()]
        for field in self.field_values:
            identifier = self.modifier + '-' + field.title
            field.content.element_id = identifier
            content.append((Label(field.title, label_for=identifier), field.content))
        content.append((Label('Published', label_for='toggle-published'), Input(element_id='toggle-published',input_type='radio', value='1', name='publish')))
        table = TableElement(*content)
        if 'destination' in self._url.get_query:
            dest = '?destination=' + self._url.get_query['destination'][0]
        else:
            dest = ''
        return str(FormElement(table, action=str(self._url) + dest))

    def handle_fields(self):
        for field in self.field_handlers:
            field_value = field.field
            self.field_values.append(field_value)
            self.integrate(field_value)
        return True

    def process_query(self):
        for field in self.field_handlers:
            field.process_post()

    def validate_inputs(self):
        for field in self.field_handlers:
            if not field.validate_inputs():
                raise ValueError

    def assign_inputs(self):
        for field in self.field_handlers:
            for key in field.get_post_query_keys():
                if not key in self._url.post_query:
                    raise KeyError
                field.query[key] = [parse.unquote_plus(a) for a in self._url.post_query[key]]

    def compile(self):
        self.get_page_information()
        self._page = Page(self._url, self.page_title)
        if self.theme:
            self._page.used_theme = self.theme
        self.get_fields()
        if self._is_post:
            self.process_post()
        self.handle_fields()
        self.assign_content()
        self._is_compiled = True
        return 200

    def process_post(self):
        self.assign_inputs()
        self.validate_inputs()
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
        self.db.update(self._url.page_type, {'page_title': self.page_title, 'published': published})


class AddFieldBasedContentHandler(EditFieldBasedContentHandler):

    def __init__(self, url, db, modules):
        super().__init__(url, db, modules)
        self.modifier = 'add'

    def get_page_information(self):
        new_id = self.db.largest_id(self._url.page_type) + 1
        self._url.page_id = new_id
        if not 'ct' in self._url.get_query:
            raise ValueError
        self.content_type = self._url.get_query['ct']
        self.page_title = 'Add new ' + self._url.page_type + ' page'

    def create_page(self):
        self.page_title = parse.unquote_plus(self._url.post_query['title'][0])
        if 'publish' in self._url.post_query.keys():
            published = True
        else:
            published = False
        self.db.insert(self._url.page_type, ('id', 'content_type', 'page_title', 'creator', 'published'), (self._url.page_id, self.content_type, self.page_title, self.user, published))

    def process_post(self):
        self.assign_inputs()
        self.validate_inputs()
        self.create_page()
        self.process_query()

    def title_input(self):
        return [Label('Title', label_for='edit-title'), Input(element_id='edit-title', name='title', required=True)]


class FieldInfo:

    def __init__(self, field_name, handler_module_name, weight, machine_name, modules, modifier='show'):
        self.modules = modules
        self.field_name = field_name
        self.handler_module = self.get_handler(handler_module_name)
        self.weight = weight
        self.machine_name = machine_name

    def get_handler(self, module_name):
        self.modules[module_name].field_handler(self.field_name, page_id, modifier)
