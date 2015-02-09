import binascii
from framework.middleware import csrf

__author__ = 'Justus Adam'

import unittest


class TestFormToken(unittest.TestCase):
    def test_form(self):
        csrf.ARToken.create_table()
        fid, test_token = csrf.new()
        dbobj = csrf.ARToken.get(form_id=fid)
        tokenfield = binascii.hexlify(dbobj.token).decode()
        self.assertIsInstance(tokenfield, type(test_token))
        self.assertEqual(tokenfield, test_token)
        self.assertEqual(csrf._validate(fid=fid, token=test_token), True)


if __name__ == '__main__':
    unittest.main()
