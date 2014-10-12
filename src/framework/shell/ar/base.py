from framework.shell.ar.data import Column
from ..database import escape, DatabaseError
from .data import Table
from itertools import chain
from ..connector import Connector

__author__ = 'justusadam'


class AR(Connector):

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
    return SimpleARTable(self, name)


class ARTable(AR):

  name = None
  table = None

  def __init__(self, ar_database):
    assert isinstance(ar_database, ARDatabase)
    super().__init__(ar_database.database)
    self.ar_database = ar_database

  def keys(self):
    pass

  def row(self, **identifiers):
    pass

  def insert(self, pairing, identifiers):
    pass

  def update(self, pairing, identifier):
    pass

  def select(self, rows, identifiers):
    pass

  def join_condition(self, identifiers):
    return ' and '.join(list(a + '=' + escape(identifiers[a]) for a in identifiers))


class SimpleARTable(ARTable):

  @property
  def table(self):
    return self.columns

  def __init__(self, ar_database, name):
    super().__init__(ar_database)
    self.name = name
    self.columns = Table(*self._get_cols(name))

  def keys(self):
    return self.table.db_keys()

  def _get_cols(self, table):
    data = self.db.show_columns(table=table)
    return list(Column(*b) for b in data)

  def row(self, **identifiers):
    return ARRow(self, **identifiers)

  def insert(self, pairing, identifiers):
    self.db.insert(self.name, pairing, 'where ' + self.join_condition(identifiers))

  def update(self, pairing, identifier):
    self.db.update(self.name, pairing, 'where ' + self.join_condition(identifier))

  def select(self, rows, identifiers):
    return self.db.select(', '.join(rows), self.name, 'where ' + self.join_condition(identifiers) + ';').fetchone()


class CompoundARTable(ARTable):

  tables = {}

  def __init__(self, ar_database, *names):
    super().__init__(ar_database)
    for name in names:
      self.tables[name] = SimpleARTable(ar_database, name)

  def row(self, **identifiers):
    return ARRow(self, **identifiers)

  def keys(self):
    return set(chain(*(a.keys() for a in self.tables.values())))

  @property
  def table(self):
    return {a.table for a in self.tables}


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
      result = self.ar_table.select(items, self._key_values)
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
    else:
      raise KeyError

  def save(self):
    if self.updated:
      if self.exists:
        self._update()
      else:
        self._insert()
        self.exists = True
      self.updated = []

  def _update(self):
    self.ar_table.update(dict([[a, self.values[a]] for a in self.updated]), self._key_values)

  def _insert(self):
    pairing = dict([[a, self.values[a]] for a in self.updated])
    missing_keys = []
    for key in filter(lambda a: self.table[a].default is None and 'auto_increment' not in self.table[a].extra, self.table):
      if key not in pairing:
        missing_keys.append(key)
    if missing_keys:
      print('missing columns with no default argument: ' + ' '.join(missing_keys))
      raise ValueError
    self.ar_table.insert(pairing,  self._key_values)
    self._get_data()