from dynct.modules.form import tokens

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
    def test_form(self):
        test_token, fid = tokens.new()
        self.assertEqual(tokens._validate(fid=fid, token=test_token), True)


if __name__ == '__main__':
    unittest.main()
