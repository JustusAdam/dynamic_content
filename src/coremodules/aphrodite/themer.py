import os
from pathlib import Path
from coremodules.olymp import Database
from coremodules.olymp.database import escape
from tools.config_tools import read_config

__author__ = 'justusadam'


class Theme:

    def __init__(self, page):
        self.page = page
        self.db = Database()
        self.theme_path = self.get_theme_path()
        self.theme_config = read_config(self.theme_path + '/config.json')

    def get_theme_path(self):
        return read_config(self.get_my_folder() + '/config.json')['active_theme_path']

    def get_my_folder(self):
        return str(Path(__file__).parent)