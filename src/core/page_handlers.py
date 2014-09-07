from pathlib import Path

from core.base_handlers import PageHandler

from .page import Page
from core.database import escape


__author__ = 'justusadam'


class FileHandler(PageHandler):

    def __init__(self, url, bootstrap):
        super().__init__(url)
        self.page_type = 'file'
        self._document = ''
        self.bootstrap = bootstrap

    def compile(self):
        return self.parse_path()

    @property
    def encoded_document(self):
        return self._document

    def parse_path(self):
        if len(self._url.path) < 2:
            return 403
        basedirs = self.bootstrap.FILE_DIRECTORIES[self._url.path[0]]
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
                            print('yes]]')
                            self.encoding = 'ogg/vorbis'
                        if suffix == '.png':
                            self.encoding = 'png'
                        if suffix in content_types:
                            self.content_type = content_types[suffix]
                    self._document = filepath.open('rb').read()
                    self._has_document = True
                    return self.response
            except FileNotFoundError:
                pass
        return 404


class BasicPageHandler(PageHandler):
    def __init__(self, url, db, modules):
        super().__init__(url)
        self._page = Page(url)
        self.db = db
        self.modules = modules

    def get_content_handler(self):
        db_result = self.db.select('handler_module', 'content_handlers', 'where path_prefix = ' +
                                    escape(self._url.page_type)).fetchone()
        if db_result:
            handler_module = db_result[0]
        else:
            return None
        handler = self.modules[handler_module].content_handler
        return handler

    def get_theme_handler(self):
        return self.modules['aphrodite'].theme_handler


    def compile(self):
        content_handler = self.get_content_handler()(self._url, self.db, self.modules)
        if not content_handler.compile():
            self.response = 404
            return 404
        page = content_handler.page
        theme_handler = self.get_theme_handler()(page)
        if not theme_handler.compile():
            self.response = 404
            return 404
        self._document = theme_handler.document
        return self.response