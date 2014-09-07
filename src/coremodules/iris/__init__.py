from core.content_handler import FieldBasedContentHandler, EditFieldBasedContentHandler
from core.field_handler import BaseFieldHandler, EditBaseFieldHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'

def content_handler(url, db, modules):
    if url.page_modifier in ['add', 'edit']:
        return EditFieldBasedContentHandler(url, db, modules)
    return FieldBasedContentHandler(url, db, modules)

def field_handler(field_name, db, page_id):
    return BaseFieldHandler(db, page_id, field_name)

def edit_field_handler(field_name, db, page_id):
    return EditBaseFieldHandler(db, page_id, field_name)