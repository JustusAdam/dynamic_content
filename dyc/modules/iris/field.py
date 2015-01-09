from dyc import core
from dyc.errors.exceptions import DCException
from dyc.modules import wysiwyg
from . import model
from dyc.util import lazy, html


__author__ = 'Justus Adam'

DEFAULT_FIELD_HANDLER_NAME = 'FieldHandler'


@core.Component('FieldTypes')
class Fields(lazy.Loadable):
    def __init__(self):
        super().__init__()
        self._inner = None

    @staticmethod
    def _get_handler(string:str):
        module, *function = string.split('.', 1)
        return getattr(core.get_component('Modules')[module],
            function if function else DEFAULT_FIELD_HANDLER_NAME)

    def load(self):
        self._inner = {
            a.machine_name: (self._get_handler(a.handler)
                for a in model.FieldType.select())
        }

    @lazy.ensure_loaded
    def __getitem__(self, item):
        return self._inner[item]


@core.inject(fields='fields')
def field(field_type, fields):
    def inner(class_):
        fields[field_type] = class_
        return class_

    return inner


class FieldExists(DCException):
    pass


class _Field(object):
    def __init__(self, config, page_type):
        super().__init__()
        self.config = config
        self.page_type = page_type

    @property
    def name(self):
        return self.config.field_type.machine_name

    def access(self, page_id):
        db_obj = self.from_db(page_id)
        return dict(content=html.ContainerElement(db_obj.content,
            classes={'field', 'field-' + self.name}),
            title=self.get_field_title()
            )

    def edit(self, page_id):
        try:
            db_obj = self.from_db(page_id)
            return dict(
                name=self.name,
                content=wysiwyg.WysiwygTextarea(db_obj.content,
                    classes={'field', 'field-' + self.name, 'edit'}))
        except:
            raise

    def from_db(self, page_id):
        return model.field(self.name).get(page_id=page_id,
            page_type=self.page_type)

    def add(self, page_id):
        try:
            self.from_db(page_id)
            raise FieldExists
        except model.orm.DoesNotExist:
            return dict(name=self.name, content=wysiwyg.WysiwygTextarea(
                classes={'field', 'field-' + self.name, 'edit'}))

    def get_field_title(self):
        return self.name


Field = _Field
