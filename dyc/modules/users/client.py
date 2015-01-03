from . import users


__author__ = 'justusadam'

SESSION_TOKEN_IDENTIFIER = 'SESS'


class Information(object):
    def __init__(self, user):
        self.user = user

    @property
    def access_group(self):
        return self.user.access_group

    def check_permission(self, permission):
        result = users.check_permission(self.access_group, permission)
        if not result:
            print('Failed to authorize for ', permission)
        return result