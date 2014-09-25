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

    def auth_user(self):
        return -1

    def get_acc_grp(self, user):
        return 0

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def cookies(self):
        return self._cookies