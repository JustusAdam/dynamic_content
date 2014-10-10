from includes import log
from ..database import escape, DatabaseError
from .column import Column
from .table import Table

__author__ = 'justusadam'


class AR:

  database = None
  db = database

  def __init__(self, database):
    self.database = database

  def __del__(self):
    self.save()

  def save(self):
    pass


class ARDatabase(AR):

  def __init__(self, database):
    super().__init__(database)


class ARTable(AR):

  def __init__(self, ar_database, name):
    assert isinstance(ar_database, ARDatabase)
    super().__init__(ar_database.database)
    self.ar_database = ar_database
    self.name = name
    self.table = Table(*self._get_cols(name))

  def _get_cols(self, table):
    data = self.db.show_columns(table=table)
    return list(Column(*b) for b in data)


class ARRow(AR):

  _key_values = {}
  allowed_identifiers = []
  updated = []
  values = {}
  exists = True

  def __init__(self, table, autoretrieve=True, **identifiers):
    assert isinstance(table, ARTable)
    super().__init__(ARTable.database)
    self.table = table
    for key in identifiers:
      if key in self.allowed_identifiers:
        self._key_values[key] = identifiers[key]
      else:
        log.write_error('active record', message='identifier ' + key + ' is not allowed')

    if self._key_values and autoretrieve:
      items = self.items
      try:
        result = self.db.select(', '.join(items), self.table, 'where ' + self.identifier() + ';').fetchone()
        self.values = dict(zip(items, result))
      except (DatabaseError, Exception):
        self.exists = False

  @property
  def columns(self):
    return self.table.columns

  @property
  def _db_keys(self):
    columns = {a.name: a for a in self.columns}
    return filter(lambda a: bool(columns[a].key), self.items)

  @property
  def keys(self):
    return self._key_values

  @property
  def items(self):
    return [a.name for a in self.columns]

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
    self.db.update(self.table, dict([[a, self.values[a]] for a in self.updated]), 'where ' + self.identifier())

  def _insert(self):
    pairing = {a: None for a in self._db_keys}
    pairing.update(dict([[a, self.values[a]] for a in self.updated]))
    self.db.insert(self.table, pairing, 'where ' + self.identifier())

  def identifier(self):
    return ' '.join(list(a + '=' + escape(self._key_values[a]) for a in self._key_values))