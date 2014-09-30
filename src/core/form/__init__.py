from .database_operations import FormOperations
from .secure import SecureForm

__author__ = 'justusadam'


def prepare():
  fo = FormOperations()
  fo.init_tables()

def validate(form, user, query_or_token):
  if isinstance(query_or_token, str):
    FormOperations().validate(form, user, query_or_token)
  else:
    FormOperations().validate(form, user, query_or_token['form_token'])

