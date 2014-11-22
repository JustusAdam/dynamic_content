from dynct.backend.ar.base import ARObject
from dynct.util.time import utcnow

__author__ = 'justusadam'

USERS_TABLE_NAME = 'cms_users'
USERS_AUTH_TABLE_NAME = 'cms_user_auth'


class AccessGroup(ARObject):
    _table = 'access_groups'

    def __init__(self, machine_name, aid=-1):
        super().__init__()
        self.aid = aid
        self.machine_name = machine_name


class AccessGroupPermission(ARObject):
    _table = 'access_group_permissions'

    def __init__(self, aid, permission):
        super().__init__()
        self.aid = aid
        self.permission = permission


class Session(ARObject):
    _table = 'session'

    def __init__(self, sess_token, uid, exp_date, session_id=-1):
        super().__init__()
        self.session_id = session_id
        self.sess_token = sess_token
        self.exp_date = exp_date
        self.uid = uid


class User(ARObject):
    _table = USERS_TABLE_NAME

    def __init__(self, username, email_address, user_first_name, user_last_name, access_group, user_middle_name='', date_created=utcnow(), date_changed=utcnow(), uid=-1):
        super().__init__()
        self.username = username
        self.email_address = email_address
        self.user_first_name = user_first_name
        self.user_middle_name = user_middle_name
        self.user_last_name = user_last_name
        self.access_group = access_group
        self.date_changed = date_changed
        self.date_created = date_created
        self.uid = uid

    def update(self, **descriptors):
        self.date_changed = utcnow()
        super().update(**descriptors)


class UserAuth(ARObject):
    _table = USERS_AUTH_TABLE_NAME

    def __init__(self, uid, password, salt, id=-1):
        super().__init__()
        self.id = id
        self.uid = uid
        self.password = password
        self.salt = salt
