from core import modules
from framework.cli_info import ClientInformation, ANONYMOUS, SESSION_TOKEN_IDENTIFIER

__author__ = 'justusadam'


class ClientInfoImpl(ClientInformation):
    def __init__(self, headers):
        super().__init__(headers)
        try:
            self.auth_module = modules.Modules()['user_management']
        except KeyError:
            self.auth_module = None

    def get_acc_grp(self, user):
        if user == ANONYMOUS:
            return ANONYMOUS
        else:
            return self.auth_module.users.acc_grp(user)

    def auth_user(self):
        if self._cookies:
            if SESSION_TOKEN_IDENTIFIER in self._cookies:
                db_result = self.auth_module.session.validate_session(self._cookies[SESSION_TOKEN_IDENTIFIER].value)
                if db_result is not None:
                    return db_result
        return -1