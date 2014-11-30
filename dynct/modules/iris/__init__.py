from .content_handler import IrisController
from . import field, model

__author__ = 'justusadam'

name = 'iris'

role = 'page_handler'

path_prefix = 'iris'


def admin_handler(h_name):
    return None


def field_handler(field_name, prefix, page_id, modifier):
    handlers = {
        'access': field.BaseFieldHandler,
        'add': field.AddBaseFieldHandler,
        'edit': field.EditBaseFieldHandler
    }
    return handlers[modifier](prefix, page_id, field_name)


def post_handler(url):
    handlers = {
        'add': None,
        'edit': None
    }
    return handlers[url.page_modifier]


