from ._component import (component, get_component, call_component,
                        Component, inject, inject_method)
from . import _registry, mvc
from dyc.modules import Module
from dyc.modules.theming import Theme


__author__ = 'Justus Adam'
__version__ = '0.1'


Modules = get_component('modules')


def add_theme(name, path, enabled=False):
    return Theme.create(machine_name=name, path=path, enabled=enabled)


def get_module(name):
    return Module.get(machine_name=name)


def get_theme(name):
    if name in ('active', 'default_theme'):
        name = 'default_theme'
    return Theme.get(machine_name=name)