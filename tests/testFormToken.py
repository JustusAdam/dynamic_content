from modules.form import tokens

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
  def test_form(self):
    form_name = '/unittest'
    test_token = tokens.new(form_name)
    self.assertEqual(tokens.validate(form_name, test_token), True)


if __name__ == '__main__':
  unittest.main()
