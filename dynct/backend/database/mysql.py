"""
This file holds the adapter used to connect to the database(s). It will be expanded in the future to allow for
compatibility with more database types.

The API for accessing the database is currently not finally decided upon.

It is recommended to escape all values but not table and column names using the escape() function provided here since
thus the escaping will be custom to the database type.
"""
from dynct.util.singleton import singleton

__author__ = 'justusadam'

from pymysql import connect
from pymysql.converters import escape_item

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

    def connect(self):
        self.close()
        self._connection = connect(**self.config['database_connection_arguments'])


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