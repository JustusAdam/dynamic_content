from dycm.users import users, model

__author__ = 'Justus Adam'
__version__ = '0.1'


class Permission:
    __slots__ = 'permission'

    def __init__(self, permission):
        self.permission = permission

    def init_in_db(self):
        users.new_permission(self.permission)

    def assign(self, group):
        users.assign_permission(group, self.permission)

    def check(self, user_or_group):
        if isinstance(user_or_group, model.User):
            user_or_group = user_or_group.access_group

        users.check_permission(user_or_group, self.permission)

    def __str__(self):
        return self.permission