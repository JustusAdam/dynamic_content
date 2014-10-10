from pathlib import Path

__author__ = 'justusadam'


class DataShell:

  database = None
  db = database

  def __init__(self, database=None, path=None):
    if not database:
      from .database import Database
      self.database = Database()
    self.database = database
    self.path = Path(path)


class DataError(Exception):
  pass