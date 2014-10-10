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

  def __init__(self, **identifiers):
    for key in identifiers:
      if key in self.allowed_identifiers:
        self._key_values[key] = identifiers[key]
      else:
        log.write_error('active record', message='identifier ' + key + ' is not allowed')
    self.db = Database()
    self.columns = self._get_cols()

  @property
  def _db_keys(self):
    return filter(lambda a: bool(), self.items)

  @property
  def keys(self):
    return self._key_values

  def _get_cols(self):
    c = self.db.show_columns()
    cols = [Column(*a) for a in c]
    return cols

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

  def _update(self):
    self.db.update(self.table, dict([[a, self.values[a]] for a in self.updated]), 'where ' + self.identifier())

  def _insert(self):
    pairing = {a: None for a in self._db_keys}
    pairing = dict([[a, self.values[a]] for a in self.updated])
    self.db.insert(self.table, pairing, 'where ' + self.identifier())

  def identifier(self):
    return ' '.join(list(a + '=' + escape(self._key_values[a]) for a in self._key_values))

  def __del__(self):
    self.save()