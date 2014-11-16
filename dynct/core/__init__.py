__author__ = 'justusadam'

from . import ar
from ._registry import Modules as E

name = 'core'

role = 'core'


Modules = E()
del E

def add_content_handler(handler_name, handler, prefix):
    ar.ContentHandler(handler, handler_name, prefix).save()


def translate_alias(alias):
    query_result = ar.Alias.get(alias=alias)
    if query_result:
        return query_result.source_url
    else:
        return alias


def add_alias(source, alias):
    ar.Alias(source, alias).save()