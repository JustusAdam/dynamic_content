from core.base_handlers import ContentHandler
from core.database import escape
from core.page import Page

__author__ = 'justusadam'


class FieldBasedContentHandler(ContentHandler):

    def __init__(self, url, db, modules):
        super().__init__(url, db, modules)
        self.fields = []
        self.field_contents = []
        self.page_title = ''
        self.content_type = ''
        self.theme = ''

    def get_page_information(self):
        db_result = self.db.select(('content_type', 'page_title'), self._url.page_type, 'where id = ' + escape(self._url.page_id)).fetchone()
        if not db_result:
            return False
        (self.content_type, self.page_title) = db_result
        db_result = self.db.select('theme', 'content_types', 'where content_type_name=' + escape(self.content_type)).fetchone()
        if db_result:
            self.theme = db_result[0]
        return True


    def get_fields(self):
        db_result = self.db.select(('field_name', 'handler_module', 'weight'), 'page_fields', 'where content_type = ' + escape(self.content_type)).fetchall()
        if db_result is None:
            return False
        acc = sorted(db_result, key=lambda a: a[2])
        self.fields = acc
        return True

    def handle_fields(self):
        if not self.fields:
            if not self.get_fields():
                return False
        for name in self.fields:
            field_handler = self.modules[name[1]].field_handler(name[0], self.db, self._url.page_id)
            if not field_handler.compile():
                return False
            field = field_handler.field
            self.field_contents.append(field.content)
            self.integrate(field)
        return True

    def integrate(self, component):
        for stylesheet in component.stylesheets:
            self._page.stylesheets.add(stylesheet)
        for metatag in component.metatags:
            self._page.metatags.add(metatag)
        for script in component.scripts:
            self._page.scripts.add(script)

    def concatenate_content(self):
        content = ''
        for field in self.field_contents:
            content += str(field)
        self._page.content = content
        return True

    def compile(self):
        # executing step by step since any failing will fail all subsequent steps
        if not self.get_page_information():
            return 404
        self._page = Page(self._url, self.page_title)
        if self.theme:
            self._page.used_theme = self.theme
        if not self.get_fields():
            return 404
        if not self.handle_fields():
            return 404
        if not self.concatenate_content():
            return 404
        self._is_compiled = True
        return True