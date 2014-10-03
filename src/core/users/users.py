from .database_operations import UserOperations

__author__ = 'justusadam'


def acc_grp(user):
  return UserOperations().get_acc_grp(user)


def add_user(username, password, first_name='', middle_name='', last_name=''):
  UserOperations().add_user(username, password, 1, first_name, middle_name, last_name)


def get_info(selection):
  return UserOperations().get_users(selection)