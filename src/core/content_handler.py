from core.base_handlers import ContentHandler

__author__ = 'justusadam'


class FieldBasedContentHandler(ContentHandler):

    def __init__(self, page, db, modules):
        super().__init__(page, db, modules)
        self.fields = []
        self.field_contents = []
        self.page_title = ''
        self.content_type = ''

    def get_page_information(self):
        db_result = self.db.select(('content_type', 'title'), self._page.url.page_type, 'where id = ' + self._page.url.page_id).fetchone()
        if db_result:
            (self.content_type, self.page_title) = db_result
            return True
        return False

    def get_fields(self):
        db_result = self.db.select(('field_name', 'handler_module', 'weight'), 'page_fields', 'where content_type = ' + self.content_type)
        if not db_result:
            return False
        acc = list(db_result).sort(lambda a: a[2])
        self.fields = acc
        return True

    def handle_fields(self):
        if not self.fields:
            if not self.get_fields():
                return False
        for name in self.fields:
            field_handler = self.field_contents.append(self.modules[name[1]].field_handler(name[0], self.db))
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
        if not self.get_fields():
            return 404
        if not self.handle_fields():
            return 404
        if not self.concatenate_content():
            return 404
        self._is_compiled = True
        return True