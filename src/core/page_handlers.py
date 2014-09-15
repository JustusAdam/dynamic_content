"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

from pathlib import Path

from core import database_operations
from framework.base_handlers import PageHandler
from core.modules import Modules
from includes.bootstrap import Bootstrap
from framework.page import Page


__author__ = 'justusadam'

bootstrap = Bootstrap()


class FileHandler(PageHandler):

    def __init__(self, url):
        super().__init__(url)
        self.page_type = 'file'
        self._document = ''

    @property
    def compiled(self):
        return self.parse_path()

    @property
    def encoded(self):
        return self.compiled

    def parse_path(self):
        if len(self._url.path) < 2:
            return 403
        basedirs = bootstrap.FILE_DIRECTORIES[self._url.path[0]]
        if isinstance(basedirs, str):
            basedirs = (basedirs,)
        for basedir in basedirs:
            try:
                filepath = basedir + '/'.join([''] + self._url.path[1:])
                basedir = Path(basedir).resolve()
                filepath = Path(filepath).resolve()
                if filepath.exists():
                    if basedir not in filepath.parents:
                        return 403
                    if filepath.is_dir():
                        return 403
                    # RFE figure out what content types can occur and how to identify them here with a dict()
                    content_types = {
                        '.css': 'text/css',
                        '.mp3': 'audio/mp3',
                        '.ogg': 'audio/ogg',
                        '.png': 'img/png'
                    }
                    suffix = filepath.suffix
                    if not suffix is None:
                        if suffix == '.ogg':
                            self.encoding = 'ogg/vorbis'
                        if suffix == '.png':
                            self.encoding = 'png'
                        if suffix in content_types:
                            self.content_type = content_types[suffix]
                    return filepath.open('rb').read()
            except FileNotFoundError:
                pass
        return 404


class BasicPageHandler(PageHandler):
    def __init__(self, url):
        super().__init__(url)
        self._page = Page(url)
        self.modules = Modules()

    def get_content_handler(self):
        handler_module = database_operations.ContentHandlers().get_by_prefix(self._url.page_type)

        handler = self.modules[handler_module].content_handler
        return handler

    def get_theme_handler(self):
        return self.modules['theme_engine'].theme_handler

    @property
    def compiled(self):
        content_handler = self.get_content_handler()(self._url)

        page = content_handler.compiled
        theme_handler = self.get_theme_handler()(page)
        document = theme_handler.compiled
        return document