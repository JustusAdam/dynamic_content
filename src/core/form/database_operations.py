from core.database_operations import Operations, escape
import os
import binascii

__author__ = 'justusadam'


TOKEN_SIZE = 16


def gen_token():
  return os.urandom(TOKEN_SIZE)



class FormOperations(Operations):

  _tables = {'form_tokens'}

  _queries = {
    'mysql': {
      'add_token': 'insert into form_tokens (url, token, user) values ({form}, {token}, {user});',
      'validate': 'select user from form_tokens where user={user} and form={form} and token={token};',
      'remove': 'delete from form_tokens where where user={user} and form={form} and token={token}'
    }
  }

  def new_token(self, form, user):
    token = gen_token()
    self.execute('add_token', form=escape(form), token=escape(token), user=escape(user))
    return str(binascii.hexlify(token))

  def validate(self, form, user, token):
    token = binascii.unhexlify(token)
    self.execute('validate', user=escape(user), form=escape(form), token=escape(token))
    if self.cursor.fetchone():
      self.remove(form, user, token)
      return True
    return False

  def remove(self, form, user, token):
    assert isinstance(token, bytes)
    self.execute('remove', form=escape(form), user=escape(user), token=escape(token))