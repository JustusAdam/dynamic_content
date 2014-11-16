import sqlite3
from ._abs_sql import SQLDatabase

__author__ = 'justusadam'


class Database(SQLDatabase):
    def connect(self):
        self._connection = sqlite3.connect(**self.config['database_connection_arguments'])