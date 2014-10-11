from .column import Column

__author__ = 'justusadam'


class Table(dict):

  def __init__(self, *columns):
    kwargs = {}
    for a in columns:
      assert isinstance(a, Column)
      kwargs[a.name] = a
    super().__init__(**kwargs)

  def db_keys(self):
    return filter(lambda s: bool(self[s].key), self)