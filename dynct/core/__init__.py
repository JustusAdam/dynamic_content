from peewee import DoesNotExist
from dynct.includes import log

__author__ = 'justusadam'

from . import model
from ._registry import Modules as E
from .component import component, get_component, call_component, Component

name = 'core'

role = 'core'


Modules = E()
del E

def add_content_handler(handler_name, handler, prefix):
    return model.ContentHandler(module=handler, machine_name=handler_name, path_prefix=prefix).save()


def translate_alias(alias):
    try:
        return model.Alias.get(alias=alias).source_url
    except DoesNotExist as e:
        log.write_info(message='could not find alias ' + alias, function='translate_alias', module='core')
        return alias


def add_alias(source, alias):
    return model.Alias.create(source_url=source, alias=alias)


def add_theme(name, enabled=False):
    return model.Theme.create(machine_name=name, enabled=enabled)


def get_module(name):
    return model.Module.get(machine_name=name)


def get_theme(name):
    return model.Theme.get(machine_name=name)


def get_content_type(name):
    return model.ContentTypes.get(machine_name=name)


get_ct = get_content_type