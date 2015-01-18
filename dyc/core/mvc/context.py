from http import cookies
from . import config
from dyc.includes import settings


__author__ = 'Justus Adam'
__version__ = '0.1'


class Context(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__final = False
        self.decorator_attributes = set()
        self.headers = dict()
        self.cookies = cookies.SimpleCookie()
        self.config = config.Config()
        self.theme = settings.DEFAULT_THEME
        self.client = None

    def __setitem__(self, key, value):
        if self.__final:
            return
        dict.__setitem__(self, key, value)

    def assign_key_safe(self, key, value):
        if key in self and self[key]:
            print('key ' + key + ' already exists in model')
        else:
            self.__setitem__(key, value)

    def finalize(self):
        self.__final = True
