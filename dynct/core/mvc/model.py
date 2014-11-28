from http.cookies import SimpleCookie
from .config import Config
from dynct.includes import settings

__author__ = 'justusadam'


class Model(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__final = False
        self.decorator_attributes = set()
        self.headers = set()
        self.cookies = SimpleCookie()
        self.config = Config()
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