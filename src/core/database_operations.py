"""
Implementation of the objects holding the operations executable on the database by handlers and modules.
Used for convenience and readability as well as adaptability for different database types.

This is currently the recommended method for accessing the database to ensure convenient overview of queries.
"""
import sys
from pathlib import Path

from backend.database import escape, DatabaseError, Database
from util.config import read_config


__author__ = 'justusadam'


class Operations:
    _config_name = 'config.json'

    def __init__(self):
        self.charset = 'utf-8'
        self.db = Database()

    _queries = {}

    _tables = {}

    _cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.db.cursor()
        return self._cursor

    @property
    def tables(self):
        t = self.config['tables']
        return {k: t[k] for k in self._tables}

    @property
    def queries(self):
        return self._queries[self.db.db_type.lower()]

    def execute(self, query_name, *format_args, **format_kwargs):
        query = self.queries[query_name].format(*format_args, **format_kwargs)
        try:
            self.cursor.execute(query)
        except DatabaseError as error:
            raise DBOperationError(query, error)

    def create_table(self, table, columns):
        self.db.create_table(table, columns)

    def create_all_tables(self):
        t = self.config['tables']
        for table in self._tables:
            self.create_table(table, t[table])

    def drop_tables(self, *tables):
        self.db.drop_tables(*tables)

    def fill_tables(self):
        pass

    def drop_all_tables(self):
        for table in self._tables:
            try:
                self.drop_tables(table)
            except:
                print('Could not drop table ' + table)

    def init_tables(self):
        self.drop_all_tables()
        self.create_all_tables()
        self.fill_tables()

    @property
    def config(self):
        # I am not sure this is the most efficient way of determining the config path, but it appears to be the only one
        path = str(Path(sys.modules[self.__class__.__module__].__file__).parent / self._config_name)
        return read_config(path)


class ContentHandlers(Operations):
    _queries = {
        'mysql': {
            'add_new': 'replace into content_handlers (handler_module, handler_name, path_prefix) values ({handler_module}, {handler_name}, {path_prefix});',
            'get_by_prefix': 'select handler_module from content_handlers where path_prefix={path_prefix};'
        }
    }

    _tables = {'content_handlers'}

    def add_new(self, handler_name, handler_module, path_prefix):
        self.execute('add_new', handler_module=escape(handler_module), handler_name=escape(handler_name),
                     path_prefix=escape(path_prefix))
        self.db.commit()

    def get_by_prefix(self, prefix):
        self.execute('get_by_prefix', path_prefix=escape(prefix))
        result = self.cursor.fetchone()
        if result is None:
            raise DBOperationError('get_by_prefix', 'No Result')
        return result[0]


class ModuleOperations(Operations):
    # TODO load this from file
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

    _tables = {'modules'}

    def fill_tables(self):
        self.add_module('core', 'core', 'core')

    def get_id(self, module_name):
        self.execute('get_id', module_name=escape(module_name))
        return self.cursor.fetchone()[0]

    def create_multiple_tables(self, *tables):
        for table in tables:
            try:
                self.db.create_table(**table)
            except DatabaseError as error:
                print('Error in Database Module Operations (create_table)')
                print(error)

    def get_path(self, module):
        self.execute('get_path', module_name=escape(module))
        return self.cursor.fetchone()[0]

    def set_active(self, module):
        self.execute('set_active', module_name=escape(module))

    def add_module(self, module_name, module_path, module_role):
        self.execute('add_module', module_name=escape(module_name), module_path=escape(module_path),
                     module_role=escape(module_role))

    def update_path(self, module_name, path):
        self.execute('update_path', module_path=escape(path), module_name=escape(module_name))

    def ask_active(self, module):
        self.execute('ask_active', module_name=escape(module))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_enabled(self):
        self.execute('get_enabled')
        acc = []
        for module in self.cursor.fetchall():
            acc.append({'name': module[0], 'path': module[1]})
        return acc


class Alias(Operations):
    _queries = {
        'mysql': {
            'by_alias': 'select source_url from alias where alias={alias};',
            'by_source': 'select alias from alias where source_url={source};',
            'add_alias': 'insert into alias (alias, source_url) values ({alias}, {source});'
        }
    }

    _tables = {'alias'}

    def get_by_alias(self, alias):
        self.execute('by_alias', alias=escape(alias))
        return self.cursor.fetchone()[0]

    def get_by_source(self, source):
        self.execute('by_source', source=escape(source))
        return [a[0] for a in self.cursor.fetchall()]

    def add_alias(self, source, alias):
        self.execute('add_alias', source=escape(source), alias=escape(alias))


class ContentTypes(Operations):
    _tables = {'content_types'}

    _queries = {
        'mysql': {
            'add': 'insert into content_types (content_type_name, display_name, content_handler, theme, description) values ({content_type_name}, {display_name}, {content_handler}, {theme}, {description});',
            'get_theme': 'select theme from content_types where content_type_name={content_type};',
            'get_content_types': 'select content_type_name, display_name from content_types;',
            'get_display_name': 'select display_name from content_types where content_type_name={content_type_name};'
        }
    }

    def add(self, content_type_name, display_name, content_handler, theme, description=''):
        self.execute('add', display_name=escape(display_name), content_type_name=escape(content_type_name),
                     content_handler=escape(content_handler), theme=escape(theme), description=escape(description))

    def get_theme(self, content_type):
        self.execute('get_theme', content_type=escape(content_type))
        return self.cursor.fetchone()[0]

    def get_content_types(self):
        self.execute('get_content_types')
        return self.cursor.fetchall()

    def get_ct_display_name(self, ct_name):
        self.execute('get_display_name', content_type_name=escape(ct_name))
        return self.cursor.fetchone()[0]


class DBOperationError(Exception):
    def __init__(self, query, error):
        self.query = query
        self.err = error