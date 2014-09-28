from core.database_operations import Operations, escape

__author__ = 'justusadam'


class FormOperations(Operations):

  _tables = {'form_tokens'}

  _queries = {
    'mysql': {
    }
  }

  def add_token(self, form, user):
    pass