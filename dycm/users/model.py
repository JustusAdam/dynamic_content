from dyc.backend import orm
from dyc.util import time

__author__ = 'Justus Adam'

USERS_TABLE_NAME = 'cms_users'
USERS_AUTH_TABLE_NAME = 'cms_user_auth'


class AccessGroup(orm.BaseModel):
    machine_name = orm.CharField(unique=True)


class AccessGroupPermission(orm.BaseModel):
    group = orm.ForeignKeyField(AccessGroup)
    permission = orm.CharField()

    class Meta:
        primary_key = orm.CompositeKey('group', 'permission')


class User(orm.BaseModel):
    username = orm.CharField(unique=True)
    email_address = orm.CharField()
    first_name = orm.CharField(null=True, default=None)
    middle_name = orm.CharField(null=True, default=None)
    last_name = orm.CharField(null=True, default=None)
    access_group = orm.ForeignKeyField(AccessGroup)
    date_created = orm.DateField(default=time.utcnow)
    date_changed = orm.DateField(default=time.utcnow)


class Session(orm.BaseModel):
    token = orm.BlobField()
    expires = orm.DateField(default=time.utcnow)
    user = orm.ForeignKeyField(User)


class UserAuth(orm.BaseModel):
    uid = orm.ForeignKeyField(User)
    password = orm.BlobField()
    salt = orm.BlobField()