__author__ = 'justusadam'


class AbstractDatabase:
    """
    Abstract base class for Database Interfaces. Eventually this class should define, not implement, all methods that
    Database classes have to provide and thus define the common APT amongst the Databases. See Github Issue #3
    """
    pass

    def insert(self, into_table, pairing:dict):
        pass

    def select(self, columns, from_table, query_tail, params):
        pass

    def show_columns(self, table=''):
        pass

    def remove(self, from_table, where_condition, params):
        pass

    def update(self, table, pairing, where_condition, params):
        pass

    def drop_tables(self, *tables):
        pass

    def create_table(self, table_name, columns):
        pass

    def connect(self):
        pass

    def close(self):
        pass

    def commit(self):
        pass

    def cursor(self):
        pass

    @property
    def connected(self):
        """
        This is a value indicating whether or not a connection is present.

        This method should not be overwritten, instead one should overwrite the _check_connection() method instead.
        This property exists only for beautification reasons.

        :return: boolean
        """
        return self._check_connection()

    def _check_connection(self):
        pass

    def __del__(self):
        """
        Destructor ensures the connection is closed and queries are committed.
        :return:
        """
        if self.connected:
            self.commit()
            self.close()