from .content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler

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