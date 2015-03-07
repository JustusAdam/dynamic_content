"""Session management implementation"""

import binascii
from . import model, users
import datetime
import os
from framework.util import time


__author__ = 'Justus Adam'
__version__ = '0.2'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
SESS_TOKEN_LENGTH = 16
SESSION_INVALIDATED = 'invalid'


def new_token():
    return os.urandom(SESS_TOKEN_LENGTH)


def new_exp_time():
    return time.utcnow() - datetime.timedelta(seconds=SESSION_LENGTH)


class Session:
    """Session object with utility methods"""

    def __init__(self, user, token=None):
        assert isinstance(user, model.User)
        assert isinstance(token, bytes) or token is None
        self.user = user
        self.token = token

    @classmethod
    def start(cls, user, password):
        assert isinstance(user, model.User)
        if not authenticate_user(user, password):
            return None
        try:
            token = model.Session.get(user=user).token
        except model.orm.DoesNotExist:
            token = new_token()
            model.Session.create(token=token, user=user, expires=new_exp_time())

        return cls(user, token)

    def str_token(self):
        return binascii.hexlify(self.token).decode() if self.token is not None else None

    def close(self):
        model.Session.get(user=self.user).delete()
        self.token = None

    def is_open(self):
        return self.token is not None

    @classmethod
    def validate(cls, token):
        if isinstance(token, str) and token == SESSION_INVALIDATED:
            return None
        if isinstance(token, str):
            token = binascii.unhexlify(token.encode())

        try:
            user = model.Session.get(token=token).user
        except model.orm.DoesNotExist:
            return None
        return cls(user, token)


def start_session(uid_or_username: str, password):
    user = users.get_single_user(uid_or_username)
    return binascii.hexlify(Session.start(user, password).token).decode()


def close_session(uid_or_username):
    user = users.get_single_user(uid_or_username)
    Session(user).close()


def authenticate_user(username_or_uid, password):
    try:
        user = users.get_single_user(username_or_uid)
        auth = model.UserAuth.get(uid=user)
        return users.check_ident(password, auth.salt, auth.password)
    except model.orm.DoesNotExist:
        return False


def validate_session(token):
    session = Session.validate(token)
    return session.user if session is not None else None
