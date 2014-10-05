from .database_operations import UserOperations, AccessOperations
from includes import log

__author__ = 'justusadam'


_value_mapping = {
  'first_name': 'user_first_name',
  'last_name': 'user_last_name',
  'middle_name': 'user_middle_name',
  'email': 'email_address'
}

# do not change this value after installing
CONTROL_GROUP = 0


def check_aid(func):
  def wrapped(aid, *args):
    if not isinstance(aid, int):
      if aid.isdigit():
        aid = int(aid)
      else:
        log.write_error('users', 'permissions', 'check_permission', 'invalid argument, expected numerical, got ' + str(type(aid)))
        raise ValueError
    else:
      return func(aid, *args)
  return wrapped


def acc_grp(user):
  return UserOperations().get_acc_grp(user)

@check_aid
def check_permission(aid, permission):
  return AccessOperations().check_permission(aid, permission)


@check_aid
def assign_permission(aid, permission):
  if aid == CONTROL_GROUP:
    log.write_error('users', 'permissions', 'assign_permission', 'cannot assign permissions to control group')
  elif check_permission(aid, permission):
    log.write_warning('users', 'permissions', 'assign_permission', 'access group ' + str(aid) + ' already owns permission ' + permission)
  elif check_permission(CONTROL_GROUP, permission):
    log.write_warning('users', 'permissions', 'assign_permission', 'permission ' + permission + ' does not exist yet')
    new_permission(permission)
    assign_permission(aid, permission)
  else:
    AccessOperations().add_permission(aid, permission)


@check_aid
def revoke_permission(aid, permission):
  if aid == CONTROL_GROUP:
    log.write_error('users', 'permissions', 'assign_permission', 'cannot revoke permissions from control group')
  else:
    AccessOperations().remove_permission(aid, permission)


def new_permission(permission):
  AccessOperations().add_permission(CONTROL_GROUP, permission)


def add_user(username, password, email, first_name='', middle_name='', last_name=''):
  UserOperations().add_user(username, password, email, 1, first_name, middle_name, last_name)


def get_info(selection):
  return UserOperations().get_users(selection)


def get_single_user(uname_or_id):
  return UserOperations().get_single_user(uname_or_id)


def edit_user(user_id, **kwargs):
  acc = dict()
  for argument in kwargs:
    if argument in _value_mapping:
      acc[_value_mapping[argument]] = kwargs[argument]
    else:
      acc[argument] = kwargs[argument]
  UserOperations().edit_user(user_id, **acc)