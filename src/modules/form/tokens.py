import binascii

from modules.form.database_operations import FormOperations


__author__ = 'justusadam'


def _validate(form, token):
  return FormOperations().validate(form, binascii.unhexlify(token))

def validate(form, query_or_token):
  if isinstance(query_or_token, str):
    return _validate(form, query_or_token)
  else:
    return _validate(form, query_or_token['form_token'][0])

def new(form):
  return binascii.hexlify(FormOperations().new_token(form)).decode()