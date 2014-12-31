from . import field, model, content_handler

__author__ = 'justusadam'

name = 'iris'

role = 'page_handler'

path_prefix = 'iris'

text_field_handler = field.Field


def admin_handler(h_name):
    return None


def post_handler(url):
    handlers = {
        'add': None,
        'edit': None
    }
    return handlers[url.page_modifier]


