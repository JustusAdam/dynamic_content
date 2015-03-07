"""Session management implementation"""

import binascii
from . import model, users
import datetime
import os
from framework.includes import SettingsDict
from framework.machinery import component
from framework.util import time


__author__ = 'Justus Adam'
__version__ = '0.2'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_INVALIDATED = 'invalid'


@component.inject(SettingsDict)
def new_token(settings):
    """
    generate a new session token

    :param settings: injected settings
    :return: token
    """
    return os.urandom(settings['sess_token_length'])


@component.inject(SettingsDict)
def new_exp_time(settings):
    """
    get the timedelta until a session opened now expires

    :param settings: injected settings
    :return: timedelta
    """
    return time.utcnow() - datetime.timedelta(seconds=settings['sess_length'])


class Session:
    """Session object with utility methods"""

    __slots__ = 'user', 'token'

    def __init__(self, user, token=None):
        assert isinstance(user, model.User)
        assert isinstance(token, bytes) or token is None
        self.user = user
        self.token = token

    @classmethod
    def start(cls, user, password):
        """
        start a new session and return the cls instance corresponding

        :param user: sessions user
        :param password: users password
        :return: cls()
        """
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
        """string representation of the token"""
        return binascii.hexlify(self.token).decode() if self.token is not None else None

    def close(self):
        """remove this session from the database and delete the token"""
        model.Session.get(user=self.user).delete()
        self.token = None

    def is_open(self):
        """True if the session has a valid token"""
        return self.token is not None

    @classmethod
    def validate(cls, token):
        """
        Return a new cls instance if the token is valid

        :param token: str or bytes token
        :return: cls()
        """
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
    """start a new session for this user"""
    user = users.get_single_user(uid_or_username)
    return binascii.hexlify(Session.start(user, password).token).decode()


def close_session(uid_or_username):
    """close any open session for this user"""
    user = users.get_single_user(uid_or_username)
    Session(user).close()


def authenticate_user(username_or_uid, password):
    """try to authenticate this user"""
    try:
        user = users.get_single_user(username_or_uid)
        auth = model.UserAuth.get(uid=user)
        return users.check_ident(password, auth.salt, auth.password)
    except model.orm.DoesNotExist:
        return False


def validate_session(token):
    """
    validate a session with the corresponding token is open
    and if so return the corresponding user

    :param token: str or bytes token
    :return: user or None
    """
    session = Session.validate(token)
    return session.user if session is not None else None
