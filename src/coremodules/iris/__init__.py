from core.content_handler import FieldBasedContentHandler
from core.field_handler import BaseFieldHandler
from core.page import Page

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'

def content_handler(url, db, modules):
    return FieldBasedContentHandler(url, db, modules)

def field_handler(field_name, db, page_id):
    return BaseFieldHandler(db, page_id, field_name)