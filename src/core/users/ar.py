from framework.shell.ar import base
from framework.shell.database import Database

__author__ = 'justusadam'


USERS_TABLE_NAME = 'cms_users'
USERS_AUTH_TABLE_NAME = 'cms_user_auth'

database = base.ARDatabase(Database())
users_table = base.ARTable(database, USERS_TABLE_NAME)
user_auth_table = base.ARTable(database, USERS_AUTH_TABLE_NAME)


class BaseUser(base.ARRow):

  _auth = None
  _identifiers = {}

  @property
  def auth(self):
    if self._auth is None:
      self._auth = base.ARRow(user_auth_table, **self._identifiers)
    return self._auth

  @staticmethod
  def new(uid=None, username=''):
    return NewUser(uid, username)

class ExistingUser(BaseUser):

  def __init__(self, uname_or_uid):

    # if input is uid
    if isinstance(uname_or_uid, int):
      self._identifiers = dict(id=uname_or_uid)
    elif isinstance(uname_or_uid, str):
      if uname_or_uid.isdigit():
        self._identifiers = dict(id=int(uname_or_uid))

    # if input is username
      else:
        self._identifiers = dict(username=uname_or_uid)

    # any other (invalid) input
    else:
      raise ValueError

    super().__init__(users_table, True, **self._identifiers)

class NewUser(BaseUser):

  def __init__(self, uid=None, username=''):
    if uid:
      self._identifiers['uid'] = int(uid)
    if username:
      self._identifiers['username'] = username
    super().__init__(users_table, False, **self._identifiers)