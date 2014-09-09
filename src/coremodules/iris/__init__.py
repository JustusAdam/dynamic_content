from core.content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from core.field_handler import BaseFieldHandler, EditBaseFieldHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'

def content_handler(url, db, modules):
    if url.page_modifier == 'edit':
        return EditFieldBasedContentHandler(url, db, modules)
    elif url.page_modifier == 'add':
        return AddFieldBasedContentHandler(url, db, modules)
    return FieldBasedContentHandler(url, db, modules)


def field_handler(field_name, db, page_id):
    return BaseFieldHandler(db, page_id, field_name)


def edit_field_handler(field_name, db, page_id, modifier):
    return EditBaseFieldHandler(db, page_id, field_name, modifier)