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


def _validate(form, token):
    a = ARToken.get(url=form, token=binascii.unhexlify(token))
    if a:
        a.delete()
        return True
    else:
        return False


def validate(form, query_or_token):
    print(form)
    if isinstance(query_or_token, str):
        return _validate(form, query_or_token)
    else:
        return _validate(form, query_or_token['form_token'][0])


def new(form):
    token = gen_token()
    ARToken(form, token).save()
    return binascii.hexlify(token).decode()