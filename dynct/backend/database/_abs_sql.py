from pymysql import DatabaseError, InterfaceError, ProgrammingError
from ._abs import AbstractDatabase
from dynct import errors

__author__ = 'justusadam'


class SQLDatabase(AbstractDatabase):
    date_time_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config):
        super().__init__(config)
        self._connection = None
        self.connect()

    def connect(self):
        pass

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

    def create_table(self, table_name, columns):
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)

        cursor = self.cursor()
        cursor.execute('create table ' + ' '.join([table_name, '(' + columns + ')']) + ';')
        print('created table ' + table_name)
        cursor.close()

    def select(self, columns, from_table, where_condition, query_tail:str='', params:dict=None):
        acc = ['select']
        if isinstance(columns, (list, tuple, set)):
            columns = ', '.join(columns)
        acc += [columns, 'from', from_table]
        if where_condition:
            if not where_condition.startswith('where '):
                where_condition = 'where ' + where_condition
            acc.append(where_condition)
        if not query_tail.endswith(';'):
            query_tail += ';'
        acc.append(query_tail)
        cursor = self._connection.cursor()
        query = ' '.join(acc)
        cursor.execute(query, params)
        return cursor

    def insert(self, into_table:str, pairing:dict):

        keys = list(pairing.keys())

        rows = '(' + ', '.join(keys) + ')'
        values = '(' + ', '.join(['%(' + a + ')s' for a in keys]) + ')'
        try:
            cursor = self.cursor()
            query = 'insert into ' + ' '.join([into_table, rows, 'values', values]) + ';'
            cursor.execute(query, pairing)
            cursor.close()
        except (DatabaseError, InterfaceError, ProgrammingError) as error:
            print(error)
            raise errors.DatabaseError
        return None

    def replace(self, into_table, pairing):
        keys = list(pairing.keys())

        rows = '(' + ', '.join(keys) + ')'
        values = '(' + ', '.join(['%(' + a + ')s' for a in keys]) + ')'
        try:
            cursor = self._connection.cursor()
            query = 'replace into ' + ' '.join([into_table, rows, 'values', values]) + ';'
            print(query)
            cursor.execute(query, pairing)
            cursor.close()
        except (DatabaseError, InterfaceError, ProgrammingError) as error:
            print(error)
            raise errors.DatabaseError
        return None

    def drop_tables(self, *tables):
        print('dropping' + str(tables))
        cursor = self._connection.cursor()
        cursor.execute('drop table ' + ', '.join(tables) + ';')

    def update(self, table, pairing:dict, where_condition, params:dict):
        set_clause = ', '.join([a + '=%(set_' + a + ')s' for a in pairing])
        p = {'set_' + b:pairing[b] for b in pairing}
        s = True
        while s:
            s = False
            for key in p.keys():
                if key in params:
                    s = True
                    set_clause.replace(key, 's' + key)
                    p['s' + key] = p[key]
                    del p[key]
        params.update(p)
        if where_condition and not where_condition.startswith('where '):
            where_condition = 'where ' + where_condition + ';'
        else:
            where_condition += ';'
        query = ' '.join(['update', table, 'set', set_clause, where_condition])
        try:
            cursor = self.cursor()
            print(query)
            cursor.execute(query, params)
        except (InterfaceError, ProgrammingError, DatabaseError):
            raise errors.DatabaseError

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