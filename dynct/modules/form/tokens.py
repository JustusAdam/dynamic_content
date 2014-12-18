import binascii
import os

from dynct.modules.form.model import ARToken


__author__ = 'justusadam'

TOKEN_SIZE = 16


def gen_token():
    return os.urandom(TOKEN_SIZE)


def _validate(fid, token):
    a = ARToken.get(ARToken.form_id==fid, ARToken.token==binascii.unhexlify(token))
    if a:
        a.delete()
        return True
    else:
        return False


def validate(query):
    return _validate(query['form_id'][0], query['form_token'][0])


def new():
    fid = binascii.hexlify(gen_token()).decode()
    token = gen_token()
    ARToken.create(form_id=fid, token=token)
    return binascii.hexlify(token).decode(), fid