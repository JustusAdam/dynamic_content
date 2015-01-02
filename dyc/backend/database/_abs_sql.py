from ._abs import AbstractDatabase

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
        return bool(self._connection)

    def create_table(self, table_name, columns):
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)
        try:
            self._execute('CREATE TABLE ' + ' '.join([table_name, '(' + columns + ')']) + ';')
        except Exception:
            raise
        print('created table ' + table_name)

    def select(self, columns, from_table, where_condition, query_tail:str='', params:dict=None):
        acc = ['SELECT']
        if isinstance(columns, (list, tuple, set)):
            columns = ', '.join(columns)
        acc += [columns, 'FROM', from_table]
        if where_condition:
            if not where_condition.startswith('WHERE '):
                where_condition = 'WHERE ' + where_condition
            acc.append(where_condition)
        if not query_tail.endswith(';'):
            query_tail += ';'
        acc.append(query_tail)
        query = ' '.join(acc)
        cursor = self._execute(query, params)
        return cursor

    def insert(self, into_table:str, pairing:dict):

        keys = list(pairing.keys())

        rows = '(' + ', '.join(keys) + ')'
        values = '(' + ', '.join(['%(' + a + ')s' for a in keys]) + ')'
        try:
            query = 'INSERT INTO ' + ' '.join([into_table, rows, 'VALUES', values]) + ';'
            self._execute(query, pairing)

        except Exception as error:
            print(error)
            raise
        return None

    def replace(self, into_table, pairing):
        keys = list(pairing.keys())

        rows = '(' + ', '.join(keys) + ')'
        values = '(' + ', '.join(['%(' + a + ')s' for a in keys]) + ')'
        try:
            query = 'REPLACE INTO ' + ' '.join([into_table, rows, 'VALUES', values]) + ';'
            self._execute(query, pairing)
        except Exception as error:
            print(error)
            raise

    def drop_tables(self, *tables):
        print('dropping' + str(tables))
        self._execute(('DROP TABLE ' + ', '.join(tables) + ';'))

    def update(self, table, pairing:dict, where_condition, params:dict):
        set_clause = ', '.join([a + '=%(set_' + a + ')s' for a in pairing])
        p = {'set_' + b: pairing[b] for b in pairing}
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
        if where_condition and not where_condition.startswith('WHERE '):
            where_condition = 'WHERE ' + where_condition + ';'
        else:
            where_condition += ';'
        query = ' '.join(['UPDATE', table, 'SET', set_clause, where_condition])
        try:
            self._execute(query, params)
        except Exception:
            raise

    def alter_table(self, table, add=None, alter=None):
        pass

    def remove(self, from_table, where_condition, params):
        if where_condition:
            if not where_condition.startswith('WHERE '):
                where_condition = 'WHERE ' + where_condition
            if not where_condition.endswith(';'):
                where_condition += ';'
        query = 'delete from ' + from_table + ' ' + where_condition
        return self._execute(query, params)

    def check_connection(self):
        """
        function only used for the setup process to test whether indexing the database works
        :return:
        """
        self.connect()
        cursor = self.cursor()
        try:
            cursor.execute('SHOW TABLES')
            return True
        except Exception:
            return False

    def show_columns(self, table=''):
        if table:
            table = ' FROM ' + table
        cursor = self.cursor()
        query = 'SHOW COLUMNS' + table + ';'
        cursor.execute(query)
        return cursor.fetchall()

    def _execute(self, query, params=None):
        cursor = self.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor