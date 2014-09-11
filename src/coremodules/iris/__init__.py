from .content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def content_handler(url, db, modules):
    if url.page_modifier == 'edit':
        return EditFieldBasedContentHandler(url, db, modules)
    elif url.page_modifier == 'add':
        return AddFieldBasedContentHandler(url, db, modules)
    return FieldBasedContentHandler(url, db, modules)

handlers = {
    'show': BaseFieldHandler,
    'add': AddBaseFieldHandler,
    'edit': EditBaseFieldHandler
}

def field_handler(field_name, db, page_id, modifier):
    return handlers[modifier](db, page_id, field_name)