import binascii
from dynct.modules.form import tokens
from dynct.modules.form.model import ARToken

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
    def test_form(self):
        ARToken.create_table()
        fid, test_token = tokens.new()
        dbobj = ARToken.get(form_id=fid)
        tokenfield = binascii.hexlify(dbobj.token).decode()
        self.assertIsInstance(tokenfield, type(test_token))
        self.assertEqual(tokenfield, test_token)
        self.assertEqual(tokens._validate(fid=fid, token=test_token), True)


if __name__ == '__main__':
    unittest.main()
