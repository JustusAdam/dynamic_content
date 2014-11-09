import sqlite3
from ._abs_sql import SQLDatabase
from dynct.util.singleton import singleton

__author__ = 'justusadam'


@singleton
class Database(SQLDatabase):
    def connect(self):
        self._connection = sqlite3.connect(**self.config['database_connection_arguments'])