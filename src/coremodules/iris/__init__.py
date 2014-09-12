from .content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def content_handler(url):
    if url.page_modifier == 'edit':
        return EditFieldBasedContentHandler(url)
    elif url.page_modifier == 'add':
        return AddFieldBasedContentHandler(url)
    return FieldBasedContentHandler(url)

field_handlers = {
    'show': BaseFieldHandler,
    'add': AddBaseFieldHandler,
    'edit': EditBaseFieldHandler
}

def field_handler(field_name, page_id, modifier):
    return field_handlers[modifier](page_id, field_name)