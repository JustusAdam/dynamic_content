from core import modules
from http import cookies

__author__ = 'justusadam'


SESSION_TOKEN_IDENTIFIER = 'SESS'

UNKNOWN = -2
ANONYMOUS = -1


class ClientInformation:

    def __init__(self, headers):
        self._headers = headers
        if 'Cookie' in headers:
            self._cookies = cookies.SimpleCookie(headers['Cookie'])
        else:
            self._cookies = None
        self.auth_module = modules.Modules()['user_management']
        # If user is set to -2 it is undecided what user is used, -1 is guest/not logged id
        self._user = -2
        self._access_group = -2

    @property
    def headers(self):
        return self._headers

    @property
    def user(self):
        if self._user == UNKNOWN:
            self._user = self.auth_user()
        return self._user

    @property
    def access_group(self):
        if self._access_group == UNKNOWN:
            self._access_group = self.get_acc_grp(self.user)
        return self._access_group

    def get_acc_grp(self, user):
        if user == ANONYMOUS:
            return ANONYMOUS
        else:
            return self.auth_module.users.acc_grp(user)

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def cookies(self):
        return self._cookies

    def auth_user(self):
        if self._cookies:
            if SESSION_TOKEN_IDENTIFIER in self._cookies:
                db_result = self.auth_module.session.validate_session(self._cookies[SESSION_TOKEN_IDENTIFIER].value)
                if db_result is not None:
                    return db_result
        return -1