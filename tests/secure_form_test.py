import peewee

__author__ = 'justusadam'

import unittest
from dynct.modules.form import tokens, model
import binascii


class MyTestCase(unittest.TestCase):
    def setUp(self):
        model.ARToken.create_table(fail_silently=True)

    def test_token_storage(self):
        fid, token = tokens.new()

        result = model.ARToken.get(form_id=fid, token=binascii.unhexlify(token))

        self.assertEqual(token, binascii.hexlify(result.token).decode())

        self.assertEqual(fid, result.form_id)

    def test_validate(self):
        fid, token = tokens.new()

        self.assertEqual(type(model.ARToken.get(form_id=fid, token=binascii.unhexlify(token))), model.ARToken)

        self.assertTrue(tokens._validate(fid=fid, token=token))

        self.assertRaises(peewee.DoesNotExist, model.ARToken.get, form_id=fid, token=binascii.unhexlify(token))


if __name__ == '__main__':
    unittest.main()
