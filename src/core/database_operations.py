"""
Implementation of the objects holding the operations executable on the database by handlers and modules.
Used for convenience and readability as well as adaptability for different database types.

This is currently the recommended method for accessing the database to ensure convenient overview of queries.
"""

from core import database
from core.database import escape

__author__ = 'justusadam'


class Operations:
    def __init__(self):
        self.db = database.Database()
        self.charset = 'utf-8'
        self.cursor = self.db.cursor()

    def __del__(self):
        """
        Ensures queries are committed
        :return:
        """
        self.db.commit()

    _queries = {}

    @property
    def queries(self):
        return self._queries[self.db.db_type.lower()]

    def execute(self, query_name, *format_args, **format_kwargs):
        query = self.queries[query_name].format(*format_args, **format_kwargs)
        self.cursor.execute(query)


class ContentHandlers(Operations):

    _queries = {
        'mysql' : {
            'add_new': 'replace into content_handlers (handler_module, handler_name, path_prefix) values ({handler_module}, {handler_name}, {path_prefix});',
            'get_by_prefix': 'select handler_module from content_handlers where path_prefix={path_prefix};'
        }
    }


    def add_new(self, handler_name, handler_module, path_prefix):
        self.execute('add_new', handler_module=escape(handler_module), handler_name=escape(handler_name), path_prefix=escape(path_prefix))
        self.db.commit()

    def get_by_prefix(self, prefix):
        self.execute('get_by_prefix', path_prefix=escape(prefix))
        return self.cursor.fetchone()[0]


class Modules(Operations):

    _queries = {
        'mysql': {
            'get_id': 'select id from modules where module_name={module_name};',
            'get_path': 'select module_path from modules where module_name={module_name};',
            'set_active': 'update modules set enabled=1 where module_name={module_name};',
            'add_module': 'insert into modules (module_name, module_path, module_role) values ({module_name},{module_path},{module_role});',
            'update_path': 'update modules set module_path={module_path} where module_name={module_name};',
            'ask_active': 'select enabled from modules where module_name={module_name};',
            'get_enabled': 'select module_name, module_path from modules where enabled=1;'
        }
    }

    def get_id(self, module_name):
        self.execute('get_id', module_name=escape(module_name))
        return self.cursor.fetchone()[0]

    def create_multiple_tables(self, *tables):
        for table in tables:
            try:
                self.db.create_table(**table)
            except database.DatabaseError as error:
                print('Error in Database Module Operations (create_table)')
                print(error)

    def drop_tables(self, names):
        self.db.drop_tables(names)

    def insert_into_tables(self, values):
        if not isinstance(values, (tuple, list)):
            values = (values,)
        for value in values:
            self.db.insert(**value)

    def get_path(self, module):
        self.execute('get_path', module_name=escape(module))
        return self.cursor.fetchone()[0]

    def set_active(self, module):
        self.execute('set_active', module_name=escape(module))

    def add_module(self, module_name, module_path, module_role):
        self.execute('add_module', module_name=escape(module_name), module_path=escape(module_path), module_role=escape(module_role))

    def update_path(self, module_name, path):
        self.execute('update_path', module_path=escape(path), module_name=escape(module_name))

    def ask_active(self, module):
        self.execute('update_path', module_name=escape(module))
        return self.cursor.fetchone()[0]

    def get_enabled(self):
        self.execute('get_enabled')
        acc = []
        for module in self.cursor.fetchall():
            acc.append({'name':module[0], 'path': module[1]})
        return acc


class Alias(Operations):

    _queries = {
        'mysql': {
            'by_alias': 'select source_url from alias where alias={alias};',
            'by_source': 'select alias from alias where source_url={source};'
        }
    }

    def get_by_alias(self, alias):
        self.execute('by_alias', alias=escape(alias))
        return self.cursor.fetchone()[0]

    def get_by_source(self, source):
        self.execute('by_source', source=escape(source))
        return [a[0] for a in self.cursor.fetchall()]