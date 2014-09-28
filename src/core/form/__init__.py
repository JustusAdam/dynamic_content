from .database_operations import FormOperations

__author__ = 'justusadam'


def prepare():
  fo = FormOperations()
  fo.init_tables()