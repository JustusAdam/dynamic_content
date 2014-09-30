from core.form.database_operations import FormOperations
from core import database

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
  def setUp(self):
    self.db = database.Database()
    self.ops = FormOperations()

  def test_something(self):
    form = '/test'
    user = 1
    token = self.ops.new_token(form, user)
    self.ops.validate(form, user, token)


if __name__ == '__main__':
  unittest.main()
