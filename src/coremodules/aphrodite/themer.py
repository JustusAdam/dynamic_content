from pathlib import Path
from tools.config_tools import read_config

__author__ = 'justusadam'


class ThemeHandler:

    def __init__(self, page):
        self.page = page
        self.theme_path = self.get_theme_path()
        self.theme_config = read_config(self.theme_path + '/config.json')
        self._is_compiled = False
        self._document = None

    @property
    def document(self):
        if self._is_compiled:
            return self._document
        else:
            return None

    def get_theme_path(self):
        return read_config(self.get_my_folder() + '/config.json')['active_theme_path']

    def get_my_folder(self):
        return str(Path(__file__).parent)

    def compile(self):
        pass