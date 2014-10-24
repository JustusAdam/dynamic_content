from util.config import read_config
from errors.exceptions import InvalidInputError

__author__ = 'justusadam'


class ApplicationConfig:
    pass


class ModuleConfig:
    hooks = {}

    def __init__(self, ar_connection):
        self.ar_connection = ar_connection

class JsonBasedConfig(object):
    _path = ''
    __restricted_keys = ['__restricted_keys', '_path']

    def __init__(self):
        """
        Reads the json file, assuming it contains only a dictionary and sets an attribute for every key
        in the dictionary
        :return:
        """
        super().__init__()
        self.reset()

    def reset(self):
        d = read_config(self._path, 'json')
        assert isinstance(d, dict)
        for key in d:
            super().__setattr__(key, d[key])

    def __setattr__(self, key, value):
        if key in self.__restricted_keys:
            raise InvalidInputError
        else:
            super().__setattr__(key, value)