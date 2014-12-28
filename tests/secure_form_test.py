import peewee

__author__ = 'justusadam'

import unittest
from dynct.modules import form
import binascii


class MyTestCase(unittest.TestCase):
    def setUp(self):
        form.ARToken.create_table(fail_silently=True)

    def test_token_storage(self):
        fid, token = form.new()

        result = form.ARToken.get(form_id=fid, token=binascii.unhexlify(token))

        self.assertEqual(token, binascii.hexlify(result.token).decode())

        self.assertEqual(fid, result.form_id)

    def test_validate(self):
        fid, token = form.new()

        self.assertEqual(type(form.ARToken.get(form_id=fid, token=binascii.unhexlify(token))), form.ARToken)

        self.assertTrue(form._validate(fid=fid, token=token))

        self.assertRaises(peewee.DoesNotExist, form.ARToken.get, form_id=fid, token=binascii.unhexlify(token))


if __name__ == '__main__':
    unittest.main()
