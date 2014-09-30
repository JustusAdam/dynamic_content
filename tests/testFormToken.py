from core.form.database_operations import FormOperations
from core import database

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
  def setUp(self):
    self.db = database.Database()
    self.ops = FormOperations()
    self.ops.init_tables()

  def test_something(self):
    form = '/test'
    token = self.ops.new_token(form)
    self.ops.validate(form, token)


if __name__ == '__main__':
  unittest.main()
