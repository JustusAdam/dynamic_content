from core import modules
from http import cookies

__author__ = 'justusadam'


SESSION_TOKEN_IDENTIFIER = 'SESS'


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

    @property
    def headers(self):
        return self._headers

    @property
    def user(self):
        if self._user == -2:
            self._user = self.auth_user()
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def cookies(self):
        return self._cookies

    def auth_user(self):
        if self._cookies:
            if SESSION_TOKEN_IDENTIFIER in self._cookies:
                db_result = modules.Modules()['user_management'].session.validate_session(self._cookies[SESSION_TOKEN_IDENTIFIER].value)
                if db_result is not None:
                    return db_result
        return -1