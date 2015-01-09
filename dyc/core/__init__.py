from ._component import (component, get_component, call_component,
                        Component, inject, inject_method)
from . import model, _registry, mvc, middleware


__author__ = 'Justus Adam'
__version__ = '0.1'


Modules = get_component('modules')


def add_content_handler(handler_name, handler, prefix):
    return model.ContentHandler(module=handler, machine_name=handler_name, path_prefix=prefix).save()


def add_theme(name, enabled=False):
    return model.Theme.create(machine_name=name, enabled=enabled)


def get_module(name):
    return model.Module.get(machine_name=name)


def get_theme(name):
    return model.Theme.get(machine_name=name)


def get_content_type(name):
    return model.ContentTypes.get(machine_name=name)


get_ct = get_content_type
