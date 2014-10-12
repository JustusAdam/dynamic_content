from framework.shell.ar import base
from framework.shell.database import Database

__author__ = 'justusadam'


USERS_TABLE_NAME = 'cms_users'

users_table = base.ARTable(base.ARDatabase(Database()), USERS_TABLE_NAME)

class User(base.ARRow):

  def __init__(self, uname_or_uid=None):

    # if input is uid
    if isinstance(uname_or_uid, int):
      super().__init__(users_table, id=uname_or_uid)
    elif isinstance(uname_or_uid, str):
      if uname_or_uid.isdigit():
        super().__init__(users_table, id=int(uname_or_uid))

    # if input is username
      else:
        super().__init__(users_table, username=int(uname_or_uid))

    # if input is None (new User)
    elif uname_or_uid is None:
      super().__init__(users_table, autoretrieve=False)

    # any other (invalid) input
    else:
      raise ValueError