from core.base_handlers import ContentHandler
from core.database import escape
from core.page import Page
from coremodules.aphrodite import FormElement, TableElement
from tools.http_tools import UrlQuery

__author__ = 'justusadam'


class FieldBasedContentHandler(ContentHandler):

    def __init__(self, url, db, modules):
        super().__init__(url, db, modules)
        self.field_info = []
        self.field_values = []
        self.page_title = ''
        self.content_type = ''
        self.theme = ''
        self.field_handlers = []


    def get_page_information(self):
        db_result = self.db.select(('content_type', 'page_title'), self._url.page_type, 'where id = ' + escape(self._url.page_id)).fetchone()
        if not db_result:
            return False
        (self.content_type, self.page_title) = db_result
        db_result = self.db.select('theme', 'content_types', 'where content_type_name=' + escape(self.content_type)).fetchone()
        if db_result:
            self.theme = db_result[0]
        return True

    def get_field_info(self):
        db_result = self.db.select(('field_name', 'handler_module', 'weight'), 'page_fields', 'where content_type = ' + escape(self.content_type)).fetchall()
        if db_result is None:
            return False
        acc = sorted(db_result, key=lambda a: a[2])
        self.field_info = acc
        return True

    def handle_queries(self):
        success = True
        if self._url.post_query:
            for field_handler in self.field_handlers:
                success = success and self.handle_single_field_post(field_handler)
        if self._url.get_query:
            for field_handler in self.field_handlers:
                success = success and self.handle_single_field_get(field_handler)
        if success and 'destination' in self._url.get_query:
            return 301
        else:
            return 200

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
        if not self.field_info:
            return False
        for name in self.field_info:
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
        if not self.get_page_information():
            return 404
        self._page = Page(self._url, self.page_title)
        if self.theme:
            self._page.used_theme = self.theme
        if not self.get_field_info():
            return 404
        if not self.get_fields():
            return 404
        response = self.handle_queries()
        if response != 200:
            return response
        if not self.handle_fields():
            return 404
        if not self.assign_content():
            return 404
        self._is_compiled = True
        return 200


class EditFieldBasedContentHandler(FieldBasedContentHandler):
    def get_field_handler(self, name, module):
        return self.modules[module].edit_field_handler(name, self.db, self._url.page_id)

    def concatenate_content(self):
        content = []
        for field in self.field_values:
            content.append((field.title, field.content))
        table = TableElement(*content)
        if 'destination' in self._url.get_query:
            dest = '?destination=' + self._url.get_query['destination']
        else:
            dest = ''
        return str(FormElement(table, action=str(self._url.path) + dest))