import binascii
from dyc.modules import form

__author__ = 'justusadam'

import unittest


class TestFormToken(unittest.TestCase):
    def test_form(self):
        form.ARToken.create_table()
        fid, test_token = form.new()
        dbobj = form.ARToken.get(form_id=fid)
        tokenfield = binascii.hexlify(dbobj.token).decode()
        self.assertIsInstance(tokenfield, type(test_token))
        self.assertEqual(tokenfield, test_token)
        self.assertEqual(form._validate(fid=fid, token=test_token), True)


if __name__ == '__main__':
    unittest.main()
