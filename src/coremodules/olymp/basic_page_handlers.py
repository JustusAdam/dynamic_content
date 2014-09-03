from importlib import import_module
from pathlib import Path
import sys

from coremodules.olymp.database import Database, escape
from src.tools.config_tools import read_config


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, url):
        # TODO decide what the default page_type should be
        self.page_type = ''
        self._url = url
        self._document = ''
        self.content_type = 'text/html'
        self.response = 200
        self._has_document = False
        self.encoding = sys.getfilesystemencoding()

    @property
    def encoded_document(self):
        print('using encoding ' + self.encoding)
        return self._document.encode(self.encoding)

    @property
    def document(self):
        if self._has_document and self.response == 200:
            return self._document
        else:
            return ''

    def compile_page(self):
        return self.response


class FileHandler(PageHandler):

    def __init__(self, url):
        super().__init__(url)
        self.page_type = 'file'
        self._document = ''

    def compile_page(self):
        return self.parse_path()

    @property
    def encoded_document(self):
        return self._document

    def parse_path(self):
        if len(self._url.path) < 2:
            return 403
        config = read_config('includes/bootstrap')
        basedirs = config['FILE_DIRECTORIES'][self._url.path[0]]
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
                        '.ogg': 'audio/ogg'
                    }
                    suffix = filepath.suffix
                    if not suffix is None:
                        if suffix == '.ogg':
                            print('yes]]')
                            self.encoding = 'ogg/vorbis'
                        if suffix in content_types:
                            self.content_type = content_types[suffix]
                    self._document = filepath.open('rb').read()
                    self._has_document = True
                    return self.response
            except FileNotFoundError:
                pass
        return 404


class DBPageHandler(PageHandler):

    def __init__(self, url):
        super().__init__(url)
        self.db = Database()


class BasicPageHandler(DBPageHandler):
    def __init__(self, url):
        super().__init__(url)