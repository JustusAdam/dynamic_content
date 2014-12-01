import binascii
import os
from dynct.backend.orm import *


__author__ = 'justusadam'


class ARToken(BaseModel):
    form_id = CharField()
    token = BlobField()


TOKEN_SIZE = 16


def gen_token():
    return os.urandom(TOKEN_SIZE)


def _validate(fid, token):
    a = ARToken.get(ARToken.form_id==binascii.unhexlify(fid), ARToken.token==binascii.unhexlify(token))
    if a:
        a.delete()
        return True
    else:
        return False


def validate(query):
    return _validate(query['form_id'][0], query['form_token'][0])


def new():
    fid = gen_token()
    token = gen_token()
    ARToken.create(form_id=fid, token=token)
    return binascii.hexlify(token).decode(), binascii.hexlify(fid).decode()