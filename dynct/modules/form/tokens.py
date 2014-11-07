import binascii
import os
from dynct.backend.ar.base import ARObject


__author__ = 'justusadam'


class ARToken(ARObject):
    _table = 'form_tokens'
    
    def __init__(self, url, token, id=-1):
        super().__init__()
        self.id = id
        self.url = url
        self.token = token
        

TOKEN_SIZE = 16


def gen_token():
    return os.urandom(TOKEN_SIZE)


def _validate(form, token):
    return bool(ARObject.get(url=form, token=binascii.unhexlify(token)))


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