from dynct.backend.orm import *
from dynct.util.time import utcnow

__author__ = 'justusadam'

USERS_TABLE_NAME = 'cms_users'
USERS_AUTH_TABLE_NAME = 'cms_user_auth'


class AccessGroup(BaseModel):
    machine_name = CharField(unique=True)


class AccessGroupPermission(BaseModel):
    group = ForeignKeyField(AccessGroup)
    permission = CharField()
    class Meta:
        primary_key = CompositeKey('group', 'permission')


class User(BaseModel):
    username = CharField(unique=True)
    email_address = CharField()
    first_name = CharField(null=True, default=None)
    middle_name = CharField(null=True, default=None)
    last_name = CharField(null=True, default=None)
    access_group = ForeignKeyField(AccessGroup)
    date_created = DateField(default=utcnow())
    date_changed = DateField(default=utcnow())


class Session(BaseModel):
    token = BlobField()
    expires = DateField(default=utcnow())
    user = ForeignKeyField(User)


class UserAuth(BaseModel):
    uid = ForeignKeyField(User)
    password = BlobField()
    salt = BlobField()