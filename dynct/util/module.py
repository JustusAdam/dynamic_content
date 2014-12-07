from importlib import import_module

__author__ = 'justusadam'


def import_by_path(path:str):
    path = path[:-3] if path.endswith('.py') else path
    return import_module(path.replace('/', '.'))