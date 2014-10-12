from framework.shell.ar import base
from framework.shell.database import Database

__author__ = 'justusadam'


USERS_TABLE_NAME = 'cms_users'
USERS_AUTH_TABLE_NAME = 'cms_user_auth'

database = base.ARDatabase(Database())

user_auth_table = base.ARTable(database, USERS_AUTH_TABLE_NAME)


class UserTable(base.ARTable):
  def __init__(self):
    super().__init__(database, USERS_TABLE_NAME)

  def new(self, uid=None, username=''):
    return NewUser(self, uid, username)


class BaseUser(base.ARRow):

  def __init__(self, table, autoretrieve, **identifiers):
    super().__init__(table, autoretrieve, **identifiers)

  _auth = None
  _identifiers = {}

  @property
  def auth(self):
    if self._auth is None:
      self._auth = base.ARRow(user_auth_table, **self._identifiers)
    return self._auth

  def new(self, uid=None, username=''):
    return NewUser(self.ar_table, uid, username)

class ExistingUser(BaseUser):

  def __init__(self, table, uname_or_uid):

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

    super().__init__(table, True, **self._identifiers)

class NewUser(BaseUser):

  def __init__(self, table, uid=None, username=''):
    if uid:
      self._identifiers['uid'] = int(uid)
    if username:
      self._identifiers['username'] = username
    super().__init__(table, False, **self._identifiers)


class UserGroup(base.ARRow):
  pass