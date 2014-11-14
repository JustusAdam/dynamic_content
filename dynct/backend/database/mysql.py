"""
This file holds the adapter used to connect to the database(s). It will be expanded in the future to allow for
compatibility with more database types.

The API for accessing the database is currently not finally decided upon.

It is recommended to escape all values but not table and column names using the escape() function provided here since
thus the escaping will be custom to the database type.
"""
from dynct.util.singleton import singleton

__author__ = 'justusadam'

from mysql.connector import connect
from mysql.connector import InternalError

from ._abs_sql import SQLDatabase


@singleton
class Database(SQLDatabase):
    """
    Implementation of the abstract Database for mysql databases.
    """

    def __init__(self, config):
        super().__init__(config)
        self.charset = 'utf-8'
        self.db_type = self.config['database_type']
        self._cursors = []

    def cursor(self):
        c = super().cursor()
        self._cursors.append(c)
        return c

    def connect(self):
        self.close()
        self._connection = connect(**self.config['database_connection_arguments'])

    def _execute(self, query, params=None):
        try:
            return super()._execute(query,params)
        except InternalError as e:
            raise e