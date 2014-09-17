from .content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler
from . import database_operations as dbo

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def content_handler(url):
    handlers = {
        'edit': EditFieldBasedContentHandler,
        'show': FieldBasedContentHandler,
        'add': AddFieldBasedContentHandler
    }
    return handlers[url.page_modifier](url)


def field_handler(field_name, path_prefix, page_id, modifier):
    handlers = {
        'show': BaseFieldHandler,
        'add': AddBaseFieldHandler,
        'edit': EditBaseFieldHandler
    }
    return handlers[modifier](path_prefix, page_id, field_name)


def prepare():
    ct = dbo.ContentTypes()
    ct.init_tables()
    f = dbo.Fields()
    f.init_tables()
    conf = ct.config
    page_id = ct.add_page(**conf)
    f.add_field(table='body',page_id=page_id, path_prefix=conf['page_type'], content=conf['body'])