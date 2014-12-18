from dynct.core.mvc import content_compiler as _cc
from dynct.modules.comp import html
from dynct.modules.comp import page
from dynct.modules import wysiwyg
from . import model

__author__ = 'justusadam'


class Field(_cc.ContentCompiler):
    _query = {}
    db_ops = None

    def __init__(self, path_prefix, page_id, machine_name):
        super().__init__()
        self.page_id = page_id
        self.machine_name = machine_name
        self.path_prefix = path_prefix

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    def compile(self):
        content = html.ContainerElement(self.process_content(), element_id='field-' + self.machine_name, classes={'field'})
        if not content:
            return False
        return page.Component(content)

    def get_field_title(self):
        return self.machine_name

    def process_content(self):
        return self.get_content()

    @property
    def post_query_keys(self):
        return []

    def process_post(self):
        pass

    @property
    def my_field(self):
        if not hasattr(self, '_my_field'):
            self._my_field = model.field(self.machine_name).get(path_prefix=self.path_prefix, page=self.page_id)
        return self._my_field

    def get_content(self):
        if not self.page_id:
            return ''
        try:
            return self.my_field.content
        except Exception as e:
            print(e)
            return ''


class BaseFieldHandler(Field):
    def __init__(self, path_prefix, page_id, machine_name):
        super().__init__(path_prefix, page_id, machine_name)


class EditBaseFieldHandler(BaseFieldHandler):
    xtra_classes = {'edit', 'long-text'}

    def __init__(self, path_prefix, page_id, machine_name):
        super().__init__(path_prefix, page_id, machine_name)

    def process_content(self):
        content = self.get_content()
        return wysiwyg.WysiwygTextarea(content, name=self.machine_name, rows=30, cols=50,
                        classes={self.machine_name} | self.xtra_classes)

    @property
    def post_query_keys(self):
        return [self.machine_name]

    def process_post(self):
        field = self.my_field
        field.content = self._query[self.machine_name][0]
        field.save()


class AddBaseFieldHandler(EditBaseFieldHandler):
    def process_content(self):
        if self.machine_name in self._query:
            return wysiwyg.WysiwygTextarea(self._query[self.machine_name][0], name=self.machine_name, rows=30, cols=50,
                            classes={self.machine_name} | self.xtra_classes)
        return wysiwyg.WysiwygTextarea(name=self.machine_name, rows=30, cols=50, classes={self.machine_name} | self.xtra_classes)

    def process_post(self):
        model.field(self.machine_name)(self.page_id, self._query[self.machine_name][0], self.path_prefix).save()


class FieldCompiler:
    pass

class AccessFieldCompiler(FieldCompiler):
    def __call__(self, path_prefix, node_id, machine_name):
        pass

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    def compile(self):
        content = html.ContainerElement(self.process_content(), element_id='field-' + self.machine_name, classes={'field'})
        if not content:
            return False
        return page.Component(content)

    def get_field_title(self):
        return self.machine_name

    def process_content(self):
        return self.get_content()

    @property
    def post_query_keys(self):
        return []

    def process_post(self):
        pass

    @property
    def my_field(self):
        if not hasattr(self, '_my_field'):
            self._my_field = model.field(self.machine_name).get(path_prefix=self.path_prefix, page=self.page_id)
        return self._my_field

    def get_content(self):
        if not self.page_id:
            return ''
        try:
            return self.my_field.content
        except Exception as e:
            print(e)
            return ''