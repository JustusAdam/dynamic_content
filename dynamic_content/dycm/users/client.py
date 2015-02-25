import logging

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
            logging.getLogger(__name__).warning(
                'Failed to authorize for %s' % permission
            )
        return result