from importlib import import_module

__author__ = 'justusadam'


def import_by_path(path:str):
    return import_module(path.replace('/', '.'))