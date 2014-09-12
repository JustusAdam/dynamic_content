from . import database_operations
from core.base_handlers import FieldHandler
from core.page import Component
from framework.html_elements import Textarea

__author__ = 'justusadam'


class BaseFieldHandler(FieldHandler):
    def __init__(self, page_id, machine_name):
        super().__init__()
        self.page_id = page_id
        self.machine_name = machine_name

    def compile(self):
        content = self.process_content()
        if not content:
            return False
        field = Component(self.get_field_title(), content=content)
        return field

    def get_field_title(self):
        return self.machine_name

    def process_content(self):
        return self.get_content()

    def get_content(self):
        if not self.page_id:
            return ''

        return database_operations.Fields().get_content(self.machine_name, self.page_id)

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
        database_operations.Fields().alter_content(self.machine_name, self.page_id, self.query[self.machine_name][0])

    def validate_inputs(self):
        return isinstance(self.query[self.machine_name][0], str)


class AddBaseFieldHandler(EditBaseFieldHandler):
    def process_content(self):
        return Textarea(name=self.machine_name, rows=7, cols=50)

    def process_post(self):
        database_operations.Fields().add_field(self.machine_name, self.page_id, self.query[self.machine_name][0])