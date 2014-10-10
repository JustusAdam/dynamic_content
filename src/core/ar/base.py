from includes import log
from ..database import Database, escape
from .column import Column

__author__ = 'justusadam'


class ActiveRecord:

  _key_values = {}
  allowed_identifiers = []
  table = ''
  updated = []
  values = {}
  exists = True
  db = Database()

  @classmethod
  def _get_cols(cls):
    c = cls.db.show_columns(cls.table)
    cols = [Column(*a) for a in c]
    return cols

  columns = _get_cols()

  def __init__(self, autoretrieve=True, **identifiers):
    for key in identifiers:
      if key in self.allowed_identifiers:
        self._key_values[key] = identifiers[key]
      else:
        log.write_error('active record', message='identifier ' + key + ' is not allowed')
    self.columns = self._get_cols()

    if self._key_values and autoretrieve:
      items = self.items
      result = self.db.select(', '.join(items), self.table, 'where ' + self.identifier() + ';').fetchone()
      self.values = {zip(items, result)}

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

  @property
  def columns(self):
    return self._columns

  @columns.setter
  def columns(self, val):
    self._columns = val

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

  def __del__(self):
    self.save()