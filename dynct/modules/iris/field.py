from . import database_operations
from dynct.core import handlers
from dynct.modules.comp.html_elements import Textarea
from dynct.modules.wysiwyg import WysiwygTextarea

__author__ = 'justusadam'


class BaseFieldHandler(handlers.field.Field):
    def __init__(self, path_prefix, page_id, machine_name):
        super().__init__(path_prefix, page_id, machine_name)
        self.db_ops = database_operations.Fields()


class EditBaseFieldHandler(BaseFieldHandler):
    xtra_classes = {'edit', 'long-text'}

    def __init__(self, path_prefix, page_id, machine_name):
        super().__init__(path_prefix, page_id, machine_name)

    def process_content(self):
        if self.machine_name in self._query:
            content = self._query[self.machine_name][0]
        else:
            content = self.get_content()
        return WysiwygTextarea(content, name=self.machine_name, rows=20, cols=50,
                        classes={self.machine_name} | self.xtra_classes)

    @property
    def post_query_keys(self):
        return [self.machine_name]

    def process_post(self):
        self.db_ops.alter_content(self.machine_name, self.path_prefix, self.page_id, self._query[self.machine_name][0])


class AddBaseFieldHandler(EditBaseFieldHandler):
    def process_content(self):
        if self.machine_name in self._query:
            return WysiwygTextarea(self._query[self.machine_name][0], name=self.machine_name, rows=7, cols=50,
                            classes={self.machine_name} | self.xtra_classes)
        return WysiwygTextarea(name=self.machine_name, rows=7, cols=50, classes={self.machine_name} | self.xtra_classes)

    def process_post(self):
        self.db_ops.add_field(self.machine_name, self.path_prefix, self.page_id, self.query[self.machine_name][0])