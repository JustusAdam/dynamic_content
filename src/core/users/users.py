from .database_operations import UserOperations

__author__ = 'justusadam'


_value_mapping = {
  'first_name': 'user_first_name',
  'last_name': 'user_last_name',
  'middle_name': 'user_middle_name',
  'email': 'email_address'
}


def acc_grp(user):
  return UserOperations().get_acc_grp(user)


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