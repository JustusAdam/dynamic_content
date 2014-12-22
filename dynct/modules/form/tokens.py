import binascii
import os

from . import model


__author__ = 'justusadam'

TOKEN_SIZE = 16

_form_identifier_name = 'form_id'

_form_token_name = 'form_token'


def gen_token():
    return os.urandom(TOKEN_SIZE)


def _validate(fid, token):
    a = model.ARToken.get(form_id=fid, token=binascii.unhexlify(token))
    if a:
        a.delete_instance()
        return True
    else:
        return False


def validate(query):
    return _validate(fid=query[_form_identifier_name][0], token=query[_form_token_name][0])


def new():
    fid = binascii.hexlify(gen_token()).decode()
    token = gen_token()
    model.ARToken.create(form_id=fid, token=token)
    return fid, binascii.hexlify(token).decode()