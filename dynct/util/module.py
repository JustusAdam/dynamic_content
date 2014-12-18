import importlib

__author__ = 'justusadam'


def import_by_path(path:str):
    path = path[:-3] if path.endswith('.py') else path
    return importlib.import_module(path.replace('/', '.'))