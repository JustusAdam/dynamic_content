from core.base_handlers import FieldHandler
from core.page import Component
from core.database import escape_item, escape, Database
from framework.html_elements import Textarea

__author__ = 'justusadam'


class BaseFieldHandler(FieldHandler):
    def __init__(self, page_id, machine_name):
        super().__init__()
        self.page_id = page_id
        self.machine_name = machine_name
        self.db = Database()

    def compile(self):
        content = self.process_content()
        if not content:
            return False
        field = Component(self.get_field_title(), content=content)
        self._field = field
        self._is_compiled = True
        return True

    def get_field_title(self):
        return self.machine_name

    def process_content(self):
        return self.get_content()

    def get_content(self):
        if not self.page_id:
            return ''
        db_result = self.db.select('content', self.machine_name, 'where page_id=' + escape_item(self.page_id, 'utf-8')).fetchone()
        if db_result:
            return db_result[0]
        else:
            return ''

    def get_post_query_keys(self):
        return []


class EditBaseFieldHandler(BaseFieldHandler):
    def __init__(self, page_id, machine_name):
        super().__init__(page_id, machine_name)
        self.query = {}

    def process_content(self):
        return Textarea(self.get_content(), name=self.machine_name, rows=7, cols=50)

    def get_post_query_keys(self):
        return [self.machine_name]

    def process_post(self):
        self.db.update(self.machine_name, {'content': self.query[self.machine_name][0]}, 'page_id =' + escape_item(self.page_id, 'utf-8'))

    def validate_inputs(self):
        return isinstance(self.query[self.machine_name][0], str)


class AddBaseFieldHandler(EditBaseFieldHandler):
    def process_content(self):
        return Textarea(name=self.machine_name, rows=7, cols=50)

    def process_post(self):
        self.db.insert(self.machine_name, ('content', 'page_id'), (self.query[self.machine_name][0], self.page_id))