"""
This file holds the adapter used to connect to the database(s). It will be expanded in the future to allow for
compatibility with more database types.

The API for accessing the database is currently not finally decided upon.

It is recommended to escape all values but not table and column names using the escape() function provided here since
thus the escaping will be custom to the database type.
"""
from dynct.util.singleton import singleton

__author__ = 'justusadam'

from pymysql import DatabaseError, connect
from pymysql.converters import escape_item

from ._abs import AbstractDatabase


def unwrap_pairing(pairing, charset):
    into_cols = []
    values = []
    for item in pairing:
        into_cols.append(item)
        values.append(escape(pairing[item], charset))

    def tstr(val):
        return '(' + ', '.join(val) + ')'

    return tstr(into_cols), tstr(values)


@singleton
class Database(AbstractDatabase):
    """
    Implementation of the abstract Database for mysql databases.
    """

    date_time_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config):
        self.config = config
        self._connection = None
        self.connect()
        self.charset = 'utf-8'
        self.db_type = self.config['database_type']

    def cursor(self):
        if not self.connected:
            self.connect()
        return self._connection.cursor()

    def commit(self):
        if self.connected:
            self._connection.commit()

    def close(self):
        if self.connected:
            self._connection.close()
            self._connection = None

    def _check_connection(self):
        if not self._connection:
            return False
        return bool(self._connection.socket)

    def connect(self):
        self.close()
        self._connection = connect(**self.config['database_connection_arguments'])

    def create_table(self, table_name, columns):
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)

        cursor = self.cursor()
        cursor.execute('create table ' + ' '.join([table_name, '(' + columns + ')']) + ';')
        print('created table ' + table_name)
        cursor.close()

    #
    # def get_module_id(self, module_name):
    # cursor = self._connection.cursor()
    # return cursor.execute('select id from modules where module_name = ' + module_name + ';')[0]

    def select(self, columns, from_table, query_tail, params):
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)
        if not query_tail.endswith(';'):
            query_tail += ';'
        cursor = self._connection.cursor()
        query = 'select ' + columns + ' from ' + from_table + ' ' + query_tail
        cursor.execute(query, params)
        return cursor

    def insert(self, into_table:str, pairing:dict):

        keys = pairing.keys()

        cursor = self._connection.cursor()
        query = 'insert into ' + ' '.join([into_table, keys, 'values', [':' + a for a in keys]]) + ';'
        print(query)
        cursor.execute(query, pairing)
        cursor.close()
        return

    def replace(self, into_table, pairing):
        keys = pairing.keys()

        cursor = self._connection.cursor()
        query = 'replace into ' + ' '.join([into_table, keys, 'values', [':' + a for a in keys]]) + ';'
        print(query)
        cursor.execute(query, pairing)
        cursor.close()
        return

    def drop_tables(self, *tables):
        print('dropping' + str(tables))
        cursor = self._connection.cursor()
        cursor.execute('drop table ' + ', '.join(tables) + ';')

    def update(self, table, pairing:dict, where_condition, params):
        set_clause = ', '.join([a + '=:' + a for a in pairing])
        if where_condition and not where_condition.startswith('where '):
            where_condition = 'where ' + where_condition + ';'
        else:
            where_condition += ';'
        cursor = self.cursor()
        # print(' '.join(['update', table, 'set', set_clause, where_condition]))
        cursor.execute(' '.join(['update', table, 'set', set_clause, where_condition]), params)

    def alter_table(self, table, add=None, alter=None):
        pass

    def remove(self, from_table, where_condition, params):
        if where_condition:
            if not where_condition.startswith('where '):
                where_condition = 'where ' + where_condition
            if not where_condition.endswith(';'):
                where_condition += ';'
        query = 'delete from ' + from_table + ' ' + where_condition
        cursor = self.cursor()
        return cursor.execute(query, params)

    def check_connection(self):
        """
        function only used for the setup process to test whether indexing the database works
        :return:
        """
        self.connect()
        cursor = self.cursor()
        try:
            cursor.execute('show tables')
            return True
        except DatabaseError:
            return False

    def show_columns(self, table=''):
        if table:
            table = ' from ' + table
        cursor = self.cursor()
        query = 'show columns' + table + ';'
        cursor.execute(query)
        return cursor.fetchall()


def escape(item, charset='utf-8'):
    """
    Escapes a value so that it can be used in a Query. The actual escape function invoked will depend on the type of
    database.

    This function can escape structures but does return a representation of them, not just the elements.
    :param item:
    :param charset: optional, specify the charset of your input
    :return:
    """
    return escape_item(item, charset)