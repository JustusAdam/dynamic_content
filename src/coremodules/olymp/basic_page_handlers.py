from pathlib import Path

from includes.database import Database
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

    @property
    def document(self):
        return self._document

    def parse_get(self, query):
        if query != '' and isinstance(query, str):
            return dict(option.split('=') for option in query.split('?'))
        else:
            return query

    def compile_page(self):
        return 200


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
                    return 200
            except FileNotFoundError:
                pass
        return 404


class DBPageHandler(PageHandler):

    def __init__(self, page_id, get_query=''):
        super().__init__(page_id=page_id, get_query=get_query)
        self.db = Database


class SimplePageHandler(DBPageHandler):
    def __init__(self, page_id, get_query=''):
        super().__init__(page_id=page_id, get_query=get_query)
        self.content_type = self.get_content_type()

    def get_content_type(self):
        return self.db.select(from_table=self.page_type, columns='content_type', query_tail='where id = ' + self.page_id)

    def get_used_fields(self):
        return sorted(self.db.select(from_table='page_fields', columns=('id', 'weight'),
                              query_tail='where content_type = ' + self.content_type), key=lambda a: a[1])