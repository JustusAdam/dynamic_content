__author__ = 'justusadam'



class AbstractDatabase:
  """
  Abstract base class for Database Interfaces. Eventually this class should define, not implement, all methods that
  Database classes have to provide and thus define the common APT amongst the Databases. See Github Issue #3
  """
  pass

  def insert(self, into_table, pairing, charset=None):
    pass

  def select(self, columns, from_table, query_tail=';'):
    pass