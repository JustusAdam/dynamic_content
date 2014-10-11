from framework.shell.ar.data import Column
from includes import log
from ..database import escape, DatabaseError
from .data import Table

__author__ = 'justusadam'


class AR:

  @property
  def db(self):
    return self.database

  def __init__(self, database):
    self.database = database

  def __del__(self):
    self.save()

  def save(self):
    pass


class ARDatabase(AR):

  def __init__(self, database):
    super().__init__(database)

  def table(self, name):
    return ARTable(self, name)


class ARTable(AR):

  @property
  def table(self):
    return self.columns

  def __init__(self, ar_database, name):
    assert isinstance(ar_database, ARDatabase)
    super().__init__(ar_database.database)
    self.ar_database = ar_database
    self.name = name
    self.columns = Table(*self._get_cols(name))

  def keys(self):
    return self.table.db_keys()

  def _get_cols(self, table):
    data = self.db.show_columns(table=table)
    return list(Column(*b) for b in data)

  def row(self, **identifiers):
    return ARRow(self, **identifiers)


class ARRow(AR):

  _key_values = {}
  updated = []
  values = {}
  exists = False

  def __init__(self, table, autoretrieve=True, **identifiers):
    assert isinstance(table, ARTable)
    super().__init__(table.database)
    self.ar_table = table
    self.table = table.table
    self.table_name = table.name
    for key in identifiers:
      self._key_values[key] = identifiers[key]

    if self._key_values and autoretrieve:
      self._get_data()

  def _get_data(self):
    items = self.items
    try:
      result = self.db.select(', '.join(items), self.table_name, 'where ' + self.identifier() + ';').fetchone()
      if result:
        self.values = dict(zip(items, result))
        self.exists = True
    except (DatabaseError, Exception):
      self.exists = False

  @property
  def columns(self):
    return self.table

  @property
  def _db_keys(self):
    columns = {a.name: a for a in self.columns}
    return filter(lambda a: bool(columns[a].key), self.items)

  @property
  def keys(self):
    return self._key_values

  @property
  def items(self):
    return [a for a in self.columns]

  def __getitem__(self, item):
    if item in self.items:
      return self.values.get(item)

  def __setitem__(self, key, value):
    if key in self.items:
      self.values[key] = value
      if key not in self.updated:
        self.updated.append(key)

  def save(self):
    if self.updated:
      if self.exists:
        self._update()
      else:
        self._insert()
        self.exists = True
      self.updated = []

  def _update(self):
    self.db.update(self.table_name, dict([[a, self.values[a]] for a in self.updated]), 'where ' + self.identifier())

  def _insert(self):
    pairing = dict([[a, self.values[a]] for a in self.updated])
    missing_keys = []
    for key in filter(lambda a: self.table[a].default is None and 'auto_increment' not in self.table[a].extra, self.table):
      if key not in pairing:
        missing_keys.append(key)
    if missing_keys:
      print('missing columns with no default argument: ' + ' '.join(missing_keys))
      raise ValueError
    self.db.insert(self.table_name, pairing, 'where ' + self.identifier())
    self._get_data()

  def identifier(self):
    return ' '.join(list(a + '=' + escape(self._key_values[a]) for a in self._key_values))