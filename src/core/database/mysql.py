"""
This file holds the adapter used to connect to the database(s). It will be expanded in the future to allow for
compatibility with more database types.

The API for accessing the database is currently not finally decided upon.

It is recommended to escape all values but not table and column names using the escape() function provided here since
thus the escaping will be custom to the database type.
"""

__author__ = 'justusadam'

from pymysql import DatabaseError, connect, ProgrammingError, InterfaceError
from pymysql.converters import escape_item

from framework.singleton import singleton

from ._abs import AbstractDatabase

def unwrap_pairing(pairing, charset):
  into_cols = []
  values = []
  for item in pairing:
    into_cols.append(item)
    values.append(escape(pairing[item], charset))

  def tstr(val):
    return '(' + ' ,'.join(val) + ')'

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

  def __del__(self):
    if self._connection:
      self._connection.commit()
      self._connection.close()
      self._connection = None

  def cursor(self):
    if not self._connection:
      self.connect()
    return self._connection.cursor()

  def commit(self):
    if self._connection:
      self._connection.commit()

  def close(self):
    if self._connection:
      self._connection.close()
      self._connection = None

  def connect(self):
    if self._connection:
      self._connection.close()
    self._connection = connect(**self.config['database_connection_arguments'])

  def create_table(self, table_name, columns):
    if isinstance(columns, (list, tuple)):
      columns = ', '.join(columns)

    cursor = self._connection.cursor()
    cursor.execute('create table ' + ' '.join([table_name, '(' + columns + ')']) + ';')
    print('created table ' + table_name)
    cursor.close()

  #
  # def get_module_id(self, module_name):
  # cursor = self._connection.cursor()
  # return cursor.execute('select id from modules where module_name = ' + module_name + ';')[0]

  def select(self, columns, from_table, query_tail=';'):
    if isinstance(columns, (list, tuple)):
      columns = ', '.join(columns)
    if not query_tail.endswith(';'):
      query_tail += ';'
    cursor = self._connection.cursor()
    query = 'select ' + columns + ' from ' + from_table + ' ' + query_tail
    cursor.execute(query)
    return cursor

  def insert(self, into_table, pairing, charset=None):
    if not charset:
      charset = self.charset

    into_cols, values = unwrap_pairing(pairing, charset)

    cursor = self._connection.cursor()
    query = 'insert into ' + ' '.join([into_table, into_cols, 'values', values]) + ';'
    print(query)
    cursor.execute(query)
    cursor.close()
    return

  def replace(self, into_table, pairing, charset=None):
    if not charset:
      charset = self.charset

    into_cols, values = unwrap_pairing(pairing, charset)

    cursor = self._connection.cursor()
    query = 'replace into ' + ' '.join([into_table, into_cols, 'values', values]) + ';'
    cursor.execute(query)
    cursor.close()
    return

  def drop_tables(self, *tables):
    print('dropping' + str(tables))
    cursor = self._connection.cursor()
    cursor.execute('drop table ' + ', '.join(tables) + ';')

  def update(self, table, pairing, where_condition='', charset=None):
    if not charset:
      charset = self.charset
    if not isinstance(pairing, dict):
      return False
    set_clause = []
    for key in pairing.keys():
      set_clause.append(key + '=' + escape_item(pairing[key], charset))
    set_clause = ', '.join(set_clause)
    if where_condition and not where_condition.startswith('where '):
      where_condition = 'where ' + where_condition + ';'
    else:
      where_condition += ';'
    cursor = self._connection.cursor()
    # print(' '.join(['update', table, 'set', set_clause, where_condition]))
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