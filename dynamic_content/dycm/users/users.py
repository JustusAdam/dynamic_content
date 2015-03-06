from framework.machinery import component
from framework.util.py34 import hashlib
import os
import logging
from framework.includes import SettingsDict
from . import model

__author__ = 'Justus Adam'

_value_mapping = {
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
CONTROL_GROUP_NR = 0

model.User.create_table(fail_silently=True)
model.AccessGroup.create_table(fail_silently=True)

# special access groups
UNKNOWN_GRP = -1  # placeholder - user group undetermined

CONTROL_GROUP = model.AccessGroup.get_or_create(
    oid=CONTROL_GROUP_NR, machine_name='control_group'
)

# Not an authenticated User
GUEST_GRP = model.AccessGroup.get_or_create(
    oid=1, machine_name='_GUEST_GROUP'
)

# Default group for users. users that have no particular group assigned to them
AUTH = model.AccessGroup.get_or_create(
    oid=2, machine_name='_AUTH'
)

# special usernames
UNKNOWN = -1  # placeholder - user undetermined

# Not an authenticated User
GUEST = model.User.get_or_create(
    oid=0, username='_GUEST', access_group=GUEST_GRP, email_address='test@test'
)


class Permission:
    """permission base class"""
    __slots__ = 'permission'

    def __init__(self, permission):
        if isinstance(permission, Permission):
            permission = permission.permission
        self.permission = permission

    def init_in_db(self):
        """add the permission to the control group"""

        result = model.AccessGroupPermission.select().where(
            model.AccessGroupPermission.group == CONTROL_GROUP_NR,
            model.AccessGroupPermission.permission == self.permission
        )
        if result.wrapped_count() == 0:
            model.AccessGroupPermission.create(
                group=CONTROL_GROUP_NR, permission=self.permission
            )
        return self

    def remove(self):
        """completely remove the permission from the database"""
        model.AccessGroupPermission.delete().where(
            model.AccessGroup.permission == self.permission
        )

    def assign(self, group):
        """
        Assign this permission to the given group

        :param group: group to assign to
        :return: permission
        """

        assert isinstance(group, model.AccessGroup)
        if group == CONTROL_GROUP_NR:
            logging.getLogger(__name__).error(
                'users, permissions, assign_permission: '
                'cannot assign permissions to control group'
            )
        elif self.check(group, strict=True):
            logging.getLogger(__name__).warning(
                'in users, permissions, assign_permission:',
                'access group {} already owns permission {}'.format(
                    group, self.permission
                )
            )
        elif not self.check(CONTROL_GROUP):
            logging.getLogger(__name__).warning(
                'users, permissions, assign_permission:',
                'permission {} does not exist yet'.format(self.permission)
            )
            new_permission(self.permission)
            assign_permission(group, self.permission)
        else:
            model.AccessGroupPermission.create(group=group, permission=group.permission)
        return self

    def revoke(self, group):
        """
        Revoke this permission from given group
        :param group:
        :return:
        """
        assert isinstance(group, model.AccessGroup)
        if group == CONTROL_GROUP_NR:
            logging.getLogger(__name__).error(
                'users, permissions, assign_permission: '
                'cannot revoke permissions from control group'
            )
        else:
            model.AccessGroupPermission(
                group=group, permission=self.permission
            ).delete_instance()

    def check(self, user_or_group, strict=False):
        """check whether given user/group possesses this permission"""
        if isinstance(user_or_group, model.User):
            user_or_group = user_or_group.access_group

        return self._check(user_or_group, strict)

    def _check(self, group, strict=False):
        personal = model.AccessGroupPermission.select().where(
            model.AccessGroupPermission.group == group,
            model.AccessGroupPermission.permission == self.permission
        )
        if group != GUEST_GRP and not strict:
            general = model.AccessGroupPermission.select().where(
                model.AccessGroupPermission.group == AUTH,
                model.AccessGroupPermission.permission == self.permission
            )
            return personal.wrapped_count() != 0 or general.wrapped_count() != 0
        else:
            return personal.wrapped_count() != 0

    @staticmethod
    def list():
        """list all initialized permissions"""
        return model.AccessGroupPermission.select(
            model.AccessGroupPermission.group == CONTROL_GROUP_NR
        )

    def __str__(self):
        return self.permission


@component.inject(SettingsDict)
def hash_password(settings, password, salt):
    """hash a password according to the settings"""
    return hashlib.pbkdf2_hmac(
        settings['hashing_algorithm'],
        password,
        salt,
        settings['hashing_rounds'],
        settings['hash_length']
    )


def check_ident(password, salt, comp_hash):
    hashed = hash_password(password.encode(), salt)
    return hashed == bytes(comp_hash)


@component.inject(SettingsDict)
def hash_and_new_salt(settings, password):
    """hash password with a new slat and return both"""
    salt = os.urandom(settings['salt_length'])
    hashed = hash_password(password.encode(), salt)
    return hashed, salt


def get_user(user: str):
    """get user object from username or id"""
    if isinstance(user, model.User):
        return user
    elif isinstance(user, int) or user.isdigit():
        return model.User.get(model.User.oid == user)
    else:
        return model.User.get(model.User.username == user)


def acc_grp(user):
    """get acces group from user or AUTH if user doesn't exist"""
    result = get_user(user)
    if result:
        return result.access_group
    else:
        return AUTH


def add_acc_grp(name, aid=None):
    """add a new access group"""
    if aid is None:
        return model.AccessGroup.create(machine_name=name)
    else:
        return model.AccessGroup.create(machine_name=name, oid=aid)


def check_permission(group, permission, strict=False):
    """check if given group possesses the permission"""
    return Permission(permission).check(group, strict)


def assign_permission(group, permission):
    """assign this permission to this group"""
    Permission(permission).assign(group)


def revoke_permission(group, permission):
    """revoke this permission from this group"""
    Permission(permission).revoke(group)


def new_permission(permission):
    """
    create a new permission with this name

    :param permission: permissions name
    :return: the new Permission instance
    """
    if not isinstance(permission, Permission):
        permission = Permission(permission)
    permission.init_in_db()
    return permission


def remove_permission(permission):
    """
    completely remove this permission from the database
    and all its assignments

    :param permission: permission name
    :return: None
    """
    Permission(permission).remove()


def add_user(username, password, email, first_name='', middle_name='', last_name='', access_group=AUTH):
    """
    Create a new user

    :param username: unique username
    :param password:
    :param email:
    :param first_name:
    :param middle_name:
    :param last_name:
    :param access_group:
    :return: User instance
    """
    a = model.User.create(
        username=username,
        email_address=email,
        first_name=first_name,
        last_name=last_name,
        access_group=access_group,
        middle_name=middle_name
    )
    passwd, salt = hash_and_new_salt(password)
    model.UserAuth.create(
        uid=a,
        password=passwd,
        salt=salt
    )
    return a


def assign_access_group(user, group):
    """assign a group to a user"""
    user = get_single_user(user)
    user.access_group = get_acc_grp(group)
    user.save()
    return user


def get_acc_grp(name_or_id:str):
    """get accesss group from name or id"""
    if isinstance(name_or_id, (int, float)) or name_or_id.isnumeric():
        return model.AccessGroup.get(oid=int(name_or_id))
    else:
        return model.AccessGroup.get(machine_name=name_or_id)


def get_info(selection):
    """get information about a selection of users"""
    return model.User.select().limit(selection)


get_single_user = get_user


def edit_user(user_id, **kwargs):
    user = model.User.get(uid=user_id)
    for argument in kwargs:
        if argument in _value_mapping:
            setattr(user, _value_mapping[argument], kwargs[argument])
        else:
            setattr(user, argument, kwargs[argument])
    user.save()
    return user
