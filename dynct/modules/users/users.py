import hashlib
import os
from dynct.includes import log, settings
from . import model

__author__ = 'justusadam'

_value_mapping = {
    'first_name': 'user_first_name',
    'last_name': 'user_last_name',
    'middle_name': 'user_middle_name',
    'email': 'email_address'
}

# The following values are special user groups and users
# and very important for the software
#
# you may assign any (integer) value to them
# as long as no two of them are the same
#
# do NOT change these values after installing
# unless you reset the database and reinstall
CONTROL_GROUP = 0


# special usernames
UNKNOWN = -1  # placeholder - user undetermined
GUEST = 0  # Not a authenticated User

# special access groups
UNKNOWN_GRP = -1  # placeholder - user group undetermined
GUEST_GRP = 1  # Not an authenticated User
AUTH = 2  # Default group for users. users that have no particular group assigned to them


def check_aid(func):
    def wrapped(aid, *args, **kwargs):
        if not isinstance(aid, int):
            if aid.isalpha():
                aid = int(aid)
            else:
                log.write_error('users', 'permissions', 'check_permission',
                                'invalid argument, expected numerical, got ' + str(type(aid)))
                raise ValueError
        return func(aid, *args, **kwargs)

    return wrapped


def check_permission(pos, name):
    def dec(func):
        def wrapped(*args, **kwargs):
            if name in kwargs:
                examine = kwargs[name]
            else:
                examine = args[pos]

            if not isinstance(examine, str):
                raise ValueError
            if '-' in examine:
                raise ValueError
            return func(*args, **kwargs)

        return wrapped

    return dec


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(settings.HASHING_ALGORITHM, password, salt, settings.HASHING_ROUNDS,
                               settings.HASH_LENGTH)


def check_ident(password, salt, comp_hash):
    hashed = hash_password(password.encode(), salt)
    return hashed == bytes(comp_hash)


def hash_and_new_salt(password):
    salt = os.urandom(settings.SALT_LENGTH)
    hashed = hash_password(password.encode(), salt)
    return hashed, salt


def get_user(user:str):
    if isinstance(user, int) or user.isdigit():
        return model.User.get(uid=user)
    else:
        return model.User.get(username=user)


def acc_grp(user):
    result = get_user(user)
    if result:
        return result.access_group
    else:
        return AUTH


def add_acc_grp(name, aid=-1):
    if aid != -1:
        model.AccessGroup(name, aid).save()
    else:
        model.AccessGroup(name).save()


# @check_permission(1, 'permission')
@check_aid
def check_permission(aid, permission, strict=False):
    if aid != GUEST_GRP and not strict:
        return bool(model.AccessGroupPermission.get(aid=aid, permission=permission)) or bool(model.AccessGroupPermission.get(aid=AUTH, permission=permission))
    else:
        return bool(model.AccessGroupPermission.get(aid=aid, permission=permission))


#@check_permission(1, 'permission')
@check_aid
def assign_permission(aid, permission):
    if aid == CONTROL_GROUP:
        log.write_error('users', 'permissions', 'assign_permission', 'cannot assign permissions to control group')
    elif check_permission(aid=aid, permission=permission, True):
        log.write_warning('users', 'permissions', 'assign_permission',
                          'access group ' + str(aid) + ' already owns permission ' + permission)
    elif not check_permission(aid=CONTROL_GROUP, permission=permission):
        log.write_warning('users', 'permissions', 'assign_permission',
                          'permission ' + permission + ' does not exist yet')
        new_permission(permission)
        assign_permission(aid, permission)
    else:
        model.AccessGroupPermission(aid=aid, permission=permission).save()


#@check_permission(1, 'permission')
@check_aid
def revoke_permission(aid, permission):
    if aid == CONTROL_GROUP:
        log.write_error('users', 'permissions', 'assign_permission', 'cannot revoke permissions from control group')
    else:
        model.AccessGroupPermission(oid=aid, permission=permission).delete_instance()


#@check_permission(0, 'permission')
def new_permission(permission):
    model.AccessGroupPermission(CONTROL_GROUP, permission).save()


#@check_permission(0, 'permission')
def remove_permission(permission):
    model.AccessGroupPermission.delete().where(model.AccessGroup.permission == permission)


def add_user(username, password, email, first_name='', middle_name='', last_name=''):
    model.User(username, email, first_name, last_name, GUEST_GRP, middle_name).save()
    passwd, salt = hash_and_new_salt(password)
    model.UserAuth(model.User.get(username=username).uid, passwd, salt).save()


def get_info(selection):
    return model.User.get_many(selection)


def get_single_user(uname_or_uid):
    return get_user(uname_or_uid)


def edit_user(user_id, **kwargs):
    user = model.User.get(uid=user_id)
    for argument in kwargs:
        if argument in _value_mapping:
            setattr(user, _value_mapping[argument], kwargs[argument])
        else:
            setattr(user, argument, kwargs[argument])
    user.save()