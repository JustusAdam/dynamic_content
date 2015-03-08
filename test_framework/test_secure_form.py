import peewee

__author__ = 'Justus Adam'

import unittest
from framework.middleware import csrf
import binascii


class MyTestCase(unittest.TestCase):
    def setUp(self):
        csrf.ARToken.create_table(fail_silently=True)

    def test_token_storage(self):
        fid, token = csrf.new()

        result = csrf.ARToken.get(form_id=fid, token=binascii.unhexlify(token.encode()))

        self.assertEqual(token, binascii.hexlify(result.token).decode())

        self.assertEqual(fid, result.form_id)

    def test_validate(self):
        fid, token = csrf.new()

        self.assertEqual(type(csrf.ARToken.get(form_id=fid, token=binascii.unhexlify(token.encode()))), csrf.ARToken)

        self.assertTrue(csrf._validate(fid=fid, token=token))

        self.assertRaises(peewee.DoesNotExist, csrf.ARToken.get, form_id=fid, token=binascii.unhexlify(token.encode()))


if __name__ == '__main__':
    unittest.main()
