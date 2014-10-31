from .database_operations import UserOperations, AccessOperations
from dynct.includes import log

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


def acc_grp(user):
    result = UserOperations().get_acc_grp(user)
    if result:
        return result[0]
    else:
        return AUTH


def add_acc_grp(name, aid=-1):
    AccessOperations().add_group(aid, name)

#@check_permission(1, 'permission')
@check_aid
def check_permission(aid, permission, strict=False):
    if aid != GUEST_GRP and not strict:
        return AccessOperations().check_permission(aid, AUTH, permission)
    else:
        return AccessOperations().check_permission(aid, None, permission)

#@check_permission(1, 'permission')
@check_aid
def assign_permission(aid, permission):
    if aid == CONTROL_GROUP:
        log.write_error('users', 'permissions', 'assign_permission', 'cannot assign permissions to control group')
    elif check_permission(aid, permission, True):
        log.write_warning('users', 'permissions', 'assign_permission',
                          'access group ' + str(aid) + ' already owns permission ' + permission)
    elif not check_permission(CONTROL_GROUP, permission):
        log.write_warning('users', 'permissions', 'assign_permission',
                          'permission ' + permission + ' does not exist yet')
        new_permission(permission)
        assign_permission(aid, permission)
    else:
        AccessOperations().add_permission(aid, permission)

#@check_permission(1, 'permission')
@check_aid
def revoke_permission(aid, permission):
    if aid == CONTROL_GROUP:
        log.write_error('users', 'permissions', 'assign_permission', 'cannot revoke permissions from control group')
    else:
        AccessOperations().remove_permission(aid, permission)

#@check_permission(0, 'permission')
def new_permission(permission):
    AccessOperations().add_permission(CONTROL_GROUP, permission)

#@check_permission(0, 'permission')
def remove_permission(permission):
    AccessOperations().remove_all_permissions(permission)


def add_user(username, password, email, first_name='', middle_name='', last_name=''):
    UserOperations().add_user(username, password, email, AUTH, first_name, middle_name, last_name)


def get_info(selection):
    return UserOperations().get_users(selection)


def get_single_user(uname_or_uid):
    return UserOperations().get_single_user(uname_or_uid)


def edit_user(user_id, **kwargs):
    acc = dict()
    for argument in kwargs:
        if argument in _value_mapping:
            acc[_value_mapping[argument]] = kwargs[argument]
        else:
            acc[argument] = kwargs[argument]
    UserOperations().edit_user(user_id, **acc)