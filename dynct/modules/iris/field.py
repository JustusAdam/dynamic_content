import peewee
from dynct import core
from dynct.errors.exceptions import DCException
from dynct.modules.comp import html
from dynct.modules import wysiwyg
from . import model, node

__author__ = 'justusadam'


@core.Component('FieldTypes')
class Fields(dict):
    pass


@core.inject_kwarg('Fields', 'fields')
def field(field_type, fields):
    def inner(class_):
        fields[field_type] = class_
        return class_
    return inner


class FieldExists(DCException):
    pass


class _Field(object):

    def __init__(self, config):
        super().__init__()
        self.config = config

    @property
    def name(self):
        return self.config.machine_name

    @property
    def page_type(self):
        return self.config.page_type

    def access(self, page_id):
        db_obj = self.from_db(page_id)
        return node.Node(content=html.ContainerElement(db_obj.content, classes={'field', 'field-' + self.name}), title=self.get_field_title())

    def edit(self, page_id):
        try:
            db_obj = self.from_db(page_id)
            return node.Node(content=wysiwyg.WysiwygTextarea(db_obj.content, classes={'field', 'field-' + self.name, 'edit'}))
        except:
            raise

    def from_db(self, page_id):
        return model.field(self.name).get(page_id=page_id, page_type=self.page_type)

    def add(self, page_id):
        try:
            self.from_db(page_id)
            raise FieldExists
        except peewee.DoesNotExist:
            return node.Node(content=wysiwyg.WysiwygTextarea(classes={'field', 'field-' + self.name, 'edit'}))

    def get_field_title(self):
        return self.name
