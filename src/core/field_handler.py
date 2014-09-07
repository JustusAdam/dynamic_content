from core.base_handlers import FieldHandler
from core.database import escape
from core.page import Component
from coremodules.aphrodite import Input

__author__ = 'justusadam'


class BaseFieldHandler(FieldHandler):
    def __init__(self, db, page_id, field_name):
        super().__init__(db)
        self.page_id = page_id
        self.field_name = field_name

    def compile(self):
        content = self.process_content()
        if not content:
            return False
        field = Component(self.get_field_title(), content=content)
        self._field = field
        self._is_compiled = True
        return True

    def get_field_title(self):
        return self.field_name

    def process_content(self):
        return self.get_content()

    def get_content(self):
        if not self.page_id:
            return ''
        db_result = self.db.select('content', self.field_name, 'where page_id=' + escape(self.page_id)).fetchone()
        if db_result:
            return db_result[0]
        else:
            return ''


class EditBaseFieldHandler(BaseFieldHandler):
    def process_content(self):
        return Input(value=self.get_content(), name=self.field_name)

    def get_post_query_keys(self):
        return tuple(self.field_name)

    def get_get_query_keys(self):
        return []

    def process_post(self, query):
        pass

    def process_get(self, query):
        pass