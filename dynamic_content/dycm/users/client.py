"""Classes and functions for interactions with information about the client"""

import logging

from . import users


__author__ = 'Justus Adam'

SESSION_TOKEN_IDENTIFIER = 'SESS'


class Information(object):
    """
    Value object containing information about the client
    """
    __slots__ = 'user',

    def __init__(self, user):
        self.user = user

    @property
    def access_group(self):
        """
        The clients access group
        :return:
        """
        return self.user.access_group

    def check_permission(self, permission):
        """
        Verify whether the user has a certain permission

        :param permission: permission to check for
        :return: Boolean
        """
        result = users.check_permission(self.access_group, permission)
        if not result:
            logging.getLogger(__name__).warning(
                'Failed to authorize for %s' % permission
            )
        return result