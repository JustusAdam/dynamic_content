__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from . import ar

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    m = Modules()
    m.reload()
    return m


def add_content_handler(handler_name, handler, prefix):
    ar.ContentHandler(handler, handler_name, prefix).save()


def prepare():
    ar.Alias('/iris/1', '/welcome').save()
    ar.Alias('/iris/1', '/').save()


def translate_alias(alias):
    query_result = ar.Alias.get(alias=alias)
    if query_result:
        return query_result.source_url
    else:
        return alias


def add_alias(source, alias):
    ar.Alias(source, alias).save()