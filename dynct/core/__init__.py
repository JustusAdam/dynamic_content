__author__ = 'justusadam'

from . import model
from ._registry import Modules as E

name = 'core'

role = 'core'


Modules = E()
del E

def add_content_handler(handler_name, handler, prefix):
    model.ContentHandler(handler, handler_name, prefix).save()


def translate_alias(alias):
    query_result = model.Alias.get(alias=alias)
    if query_result:
        return query_result.source_url
    else:
        return alias


def add_alias(source, alias):
    model.Alias(source, alias).save()