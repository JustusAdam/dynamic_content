import peewee

__author__ = 'Justus Adam'

import unittest
from dyc.modules import anti_csrf
import binascii


class MyTestCase(unittest.TestCase):
    def setUp(self):
        anti_csrf.ARToken.create_table(fail_silently=True)

    def test_token_storage(self):
        fid, token = anti_csrf.new()

        result = anti_csrf.ARToken.get(form_id=fid, token=binascii.unhexlify(token))

        self.assertEqual(token, binascii.hexlify(result.token).decode())

        self.assertEqual(fid, result.form_id)

    def test_validate(self):
        fid, token = anti_csrf.new()

        self.assertEqual(type(anti_csrf.ARToken.get(form_id=fid, token=binascii.unhexlify(token))), anti_csrf.ARToken)

        self.assertTrue(anti_csrf._validate(fid=fid, token=token))

        self.assertRaises(peewee.DoesNotExist, anti_csrf.ARToken.get, form_id=fid, token=binascii.unhexlify(token))


if __name__ == '__main__':
    unittest.main()
