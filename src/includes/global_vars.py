from importlib import import_module
from . import bootstrap


__author__ = 'justusadam'

Bootstrap = bootstrap

BOOTSTRAP = bootstrap

core_path = bootstrap.COREMODULES_DIRECTORY + '.' + bootstrap.CORE_MODULE

modules = {}

roles = {'core': import_module(core_path.replace('/', '.'))}

db = None