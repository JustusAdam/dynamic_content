from dynct.util.time import utcnow

from dynct.backend.ar.base import ARObject


__author__ = 'justusadam'


def page(name):
    class Page(ARObject):
        _table = name

        def __init__(self, content_type, page_title, creator, published, date_created=utcnow(), id=-1):
            super().__init__()
            self.id = id
            self.content_type = content_type
            self.page_title = page_title
            self.creator = creator
            self.published = published
            self.date_created = date_created

        def get_id(self):
            return self._get_one_special_value('id', 'order by id desc limit 1')
    return Page


def field(name):
    class Field(ARObject):
        _table = name + '_data'

        def __init__(self, page_id, content, path_prefix, id=-1):
            super().__init__()
            self.id = id
            self.page_id = page_id
            self.content = content
            self.path_prefix = path_prefix
    return Field


class FieldConfig(ARObject):
    _table = 'page_fields'

    def __init__(self, machine_name, field_name, content_type, handler_module, weight, description, id=-1):
        super().__init__()
        self.machine_name = machine_name
        self.field_name = field_name
        self.content_type = content_type
        self.handler_module = handler_module
        self.weight = weight
        self.description = description
        self.id = id