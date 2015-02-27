"""
Tool for convenient standard (json, yaml) config reading and writing
"""
import yaml
import json


__author__ = 'Justus Adam'
__version__ = '0.2'


loaders = {
    'yaml': yaml.load,
    'json': json.load
}

dumpers = {
    'yaml': lambda a, file: print(yaml.safe_dump(a), file=file),
    'json': json.dump
}


def guess_type(file:str):
    """
    Guess the filetype from the file ending in a form suitable for the
    loaders and dumpers dict
    :param file: file name
    :return: filetype name
    """
    a = file.rsplit('.', 1)[1]
    return {
        'yml': 'yaml'
    }.get(a, a)


def read_config(file):
    """
    Read a config file and return a dict of its contents

    :param file: filename
    :return: dict
    """
    file = str(file)
    _type = guess_type(file)
    with open(file, 'r') as f:
        return loaders[_type](f)


def write_config(obj, file):
    """
    Write data to a config file

    :param obj: parent data object (usually dict)
    :retunr: None
    """
    file = str(file)
    _type = guess_type(file)
    with open(file, 'w') as f:
        dumpers[_type](obj, f)
