import binascii
from .database_operations import FormOperations

__author__ = 'justusadam'


def _validate(form, token):
  FormOperations().validate(form, binascii.unhexlify(token))

def validate(form, query_or_token):
  if isinstance(query_or_token, str):
    _validate(form, query_or_token)
  else:
    _validate(form, query_or_token['form_token'][0])

def new(form):
  return binascii.hexlify(FormOperations().new_token(form)).decode()