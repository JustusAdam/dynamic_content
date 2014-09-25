from .database_operations import UserOperations

__author__ = 'justusadam'


def acc_grp(user):
    return UserOperations().get_acc_grp(user)