from framework.util import console
from . import users


__author__ = 'Justus Adam'

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
            console.print_warning('Failed to authorize for ', permission)
        return result