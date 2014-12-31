"""
Tool for convenient standard (json) config reading and writing
"""
import pathlib

__author__ = 'justusadam'


def read_config(path, file_type='json'):
    import json

    if isinstance(path, pathlib.Path):
        path = str(path)

    if not path.endswith('.' + file_type):
        path += '.' + file_type
    with open(path, mode='r') as file:
        return json.load(file)


def write_config(config, path, file_type='json'):
    if path.endswith('.' + file_type):
        ending = ''
    else:
        ending = '.' + file_type
    import json

    with open(path + ending, mode='w') as file:
        json.dump(config, file, indent=4)