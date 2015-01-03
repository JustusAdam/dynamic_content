import binascii
from dyc.modules import anti_csrf

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
    def test_form(self):
        anti_csrf.ARToken.create_table()
        fid, test_token = anti_csrf.new()
        dbobj = anti_csrf.ARToken.get(form_id=fid)
        tokenfield = binascii.hexlify(dbobj.token).decode()
        self.assertIsInstance(tokenfield, type(test_token))
        self.assertEqual(tokenfield, test_token)
        self.assertEqual(anti_csrf._validate(fid=fid, token=test_token), True)


if __name__ == '__main__':
    unittest.main()
