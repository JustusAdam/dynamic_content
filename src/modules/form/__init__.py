from .database_operations import FormOperations
from . import tokens


__author__ = 'justusadam'


def prepare():
  fo = FormOperations()
  fo.init_tables()

def validation_hook(url):
  if 'form_token' in url.post:
    return tokens.validate(str(url), url.post['form_token'][0])
  return True