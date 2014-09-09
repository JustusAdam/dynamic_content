from pathlib import Path

__author__ = 'justusadam'

from pymysql import DatabaseError, connect

from framework.config_tools import read_config


class Database:

    def __init__(self):
        config = read_config(str(self.get_my_folder()) + '/../config')
        self._connection = connect(**config['database_connection_arguments'])

    def __del__(self):
        self._connection.commit()
        self._connection.close()

    def create_table(self, table_name, columns):
        if isinstance(columns, (list, tuple)):
            columns = '(' + ', '.join(columns) + ')'

        cursor = self._connection.cursor()
        cursor.execute('create table ' + ' '.join([table_name, columns]) + ';')
        print('created table ' + table_name)
        cursor.close()

    def get_module_id(self, module_name):
        cursor = self._connection.cursor()
        return cursor.execute('select id from modules where module_name = ' + module_name + ';')[0]

    def get_my_folder(self):
        return str(Path(__file__).parent)

    def select(self, columns, from_table, query_tail=';'):
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)
        if not query_tail.endswith(';'):
            query_tail += ';'
        cursor = self._connection.cursor()
        query = 'select ' + columns + ' from ' + from_table + ' ' + query_tail
        cursor.execute(query)
        return cursor

    def insert(self, into_table, into_cols, values):

        values = escape(values)

        def unwrap_values(a):
            if isinstance(a, (list, tuple)):
                if isinstance(a[0], (list, tuple)):
                    return ', '.join((unwrap_values(b) for b in a))
                else:
                    return '(' + ', '.join(a) + ')'
            else:
                return '(' + a + ')'

        into_cols = unwrap_values(into_cols)
        values = unwrap_values(values)

        cursor = self._connection.cursor()
        query = 'insert into ' + ' '.join([into_table, into_cols, 'values', values]) + ';'
        cursor.execute(query)
        cursor.close()
        return

    def replace(self, into_table, into_cols, values):

        values = escape(values)

        def unwrap_values(a):
            if isinstance(a, (list, tuple)):
                if isinstance(a[0], (list, tuple)):
                    return ', '.join((unwrap_values(b) for b in a))
                else:
                    return '(' + ', '.join(a) + ')'
            else:
                return '(' + a + ')'

        into_cols = unwrap_values(into_cols)
        values = unwrap_values(values)

        cursor = self._connection.cursor()
        query = 'replace into ' + ' '.join([into_table, into_cols, 'values', values]) + ';'
        cursor.execute(query)
        cursor.close()
        return

    def drop_tables(self, tables):
        if isinstance(tables, (list, tuple)):
            tables = ', '.join(tables)
        cursor = self._connection.cursor()
        cursor.execute('drop table ' + tables + ';')

    def update(self, table, pairing, where_condition=''):
        if not isinstance(pairing, dict):
            return False
        set_clause = ''
        for key in pairing.keys():
            set_clause += key + '=' + escape(pairing[key])
        if where_condition and not where_condition.startswith('where '):
            where_condition = 'where ' + where_condition + ';'
        else:
            where_condition += ';'
        cursor = self._connection.cursor()
        cursor.execute(' '.join(['update', table, 'set', set_clause, where_condition]))

    def alter_table(self, table, add=None, alter=None):
        pass

    def remove(self, from_table, where_condition):
        if where_condition:
            if not where_condition.startswith('where '):
                where_condition = 'where ' + where_condition
            if not where_condition.endswith(';'):
                where_condition += ';'
        query = 'delete from ' + from_table + ' ' + where_condition
        cursor = self._connection.cursor()
        return cursor.execute(query)

    def check_connection(self):
        """
        function only used for the setup process to test whether indexing the database works
        :return:
        """
        cursor = self._connection.cursor()
        try:
            cursor.execute('show tables')
            return True
        except DatabaseError:
            return False


def escape(value):
    if isinstance(value, tuple):
        return tuple((escape(element) for element in value))
    elif isinstance(value, list):
        return list([escape(element) for element in value])
    elif isinstance(value, str):
        return '\'' + value.replace('\'', '\\\'') + '\''
    else:
        return escape(str(value))