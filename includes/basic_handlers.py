from includes.database import Database

__author__ = 'justusadam'


class PageHandler:
    def __init__(self, page_id, get_query=''):
        self.query = self.parse_get(get_query)
        self.page_id = page_id

    def parse_get(self, query):
        if query != '' and isinstance(query, str):
            return dict(option.split('=') for option in query.split('?'))
        else:
            return query


class FileHandler(PageHandler):

    def __init__(self, path):
        super().__init__(0)
        self.path = path
        with open(self.path, mode='r') as file:
            self.file = file.read

    def compile_page(self):
        return self.file


class DBPageHandler(PageHandler):

    def __init__(self, page_id, get_query=''):
        super().__init__(page_id=page_id, get_query=get_query)
        self.db = Database


class SimplePageHandler(DBPageHandler):
    def __init__(self, page_id, get_query=''):
        super().__init__(page_id=page_id, get_query=get_query)