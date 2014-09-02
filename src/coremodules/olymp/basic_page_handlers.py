from importlib import import_module
from pathlib import Path

from coremodules.olymp.database import Database, escape
from src.tools.config_tools import read_config


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, page_id, get_query=''):
        # TODO decide what the default page_type should be
        self.page_type = ''
        self.query = self.parse_get(get_query)
        self.page_id = page_id
        self._document = ''
        self.content_type = 'text/html'
        self.response = 200
        self._has_document = False

    @property
    def document(self):
        if self._has_document and self.response == 200:
            return self._document
        else:
            return ''

    def parse_get(self, query):
        if query != '' and isinstance(query, str):
            return dict(option.split('=') for option in query.split('?'))
        else:
            return query

    def compile_page(self):
        return self.response


class FileHandler(PageHandler):

    def __init__(self, path):
        super().__init__(0)
        self.path = path
        self.page_type = 'file'
        self._document = ''

    def compile_page(self):
        return self.parse_path()

    def parse_path(self):
        if len(self.path) < 2:
            return 403
        config = read_config('includes/bootstrap')
        basedirs = config['FILE_DIRECTORIES'][self.path[0]]
        if isinstance(basedirs, str):
            basedirs = (basedirs,)
        for basedir in basedirs:
            try:
                filepath = basedir + '/'.join([''] + self.path[1:])
                basedir = Path(basedir).resolve()
                filepath = Path(filepath).resolve()
                if filepath.exists():
                    if basedir not in filepath.parents:
                        return 403
                    if filepath.is_dir():
                        return 403
                    # RFE figure out what content types can occur and how to identify them here with a dict()
                    if filepath.name.endswith('.css'):
                        self.content_type = 'text/css'
                    self._document = filepath.open().read()
                    self._has_document = True
                    return self.response
            except FileNotFoundError:
                pass
        return 404


class DBPageHandler(PageHandler):

    def __init__(self, page_id, get_query=''):
        super().__init__(page_id=page_id, get_query=get_query)
        self.db = Database()


class BasicPageHandler(DBPageHandler):
    def __init__(self, page_id, get_query):
        super().__init__(page_id=page_id, get_query=get_query)

    def compile_page(self):
        return self.response