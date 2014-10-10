from pathlib import Path
from .ar.base import ARDatabase
from .database import Database

__author__ = 'justusadam'


class DataShell:

  def __init__(self, database=None, path=None):
    if not database:
      self.database = ARDatabase(self.__database())
    else:
      assert isinstance(database, ARDatabase)
      self.database = database
    self.path = Path(path)

  def __database(self):
    return Database()



class DataError(Exception):
  pass