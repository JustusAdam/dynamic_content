from .content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler
from . import database_operations as dbo

from core.database_operations import ContentHandlers, ContentTypes

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'

path_prefix = 'iris'


def content_handler(url):
    handlers = {
        'edit': EditFieldBasedContentHandler,
        'show': FieldBasedContentHandler,
        'add': AddFieldBasedContentHandler
    }
    return handlers[url.page_modifier](url)


def field_handler(field_name, prefix, page_id, modifier):
    handlers = {
        'show': BaseFieldHandler,
        'add': AddBaseFieldHandler,
        'edit': EditBaseFieldHandler
    }
    return handlers[modifier](prefix, page_id, field_name)


def prepare():
    ct = dbo.Pages()
    ct.init_tables()
    f = dbo.Fields()
    f.init_tables()
    conf = ct.config
    page_id = ct.add_page(**{k:conf['startpage'][k] for k in ['content_type', 'creator', 'page_title', 'published', 'page_type']})
    f.add_field(table='body', page_id=page_id, path_prefix=conf['startpage']['page_type'], content=conf['startpage']['body'])
    ContentHandlers().add_new('iris', name, path_prefix)
    ContentTypes().add('start_type', 'iris', 'active')
    f.add_field_type('body', 'Body', 'start_type', 'iris')