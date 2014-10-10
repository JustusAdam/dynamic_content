from .column import Column

__author__ = 'justusadam'


class Table(dict):

  def __init__(self, *columns):
    kwargs = {a.name:a for a in columns}
    super().__init__(**kwargs)