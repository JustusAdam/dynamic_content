import binascii
from . import model, users
import datetime
import os
from dynamic_content.util import time


__author__ = 'Justus Adam'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
SESS_TOKEN_LENGTH = 16
SESSION_INVALIDATED = 'invalid'


def new_token():
    return os.urandom(SESS_TOKEN_LENGTH)


def new_exp_time():
    return time.utcnow() - datetime.timedelta(seconds=SESSION_LENGTH)


def start_session(uid_or_username:str, password):
    if not authenticate_user(uid_or_username, password):
        return None
    user = users.get_single_user(uid_or_username)
    try:
        token = model.Session.get(user=user)
        token = token.token
    except model.orm.DoesNotExist:
        token = new_token()
        model.Session.create(token=token, user=user, expires=new_exp_time())

    return binascii.hexlify(token).decode()


def close_session(uid_or_username):
    user = users.get_single_user(uid_or_username)
    model.Session.get(user=user).delete()


def authenticate_user(username_or_uid, password):
    try:
        user = users.get_single_user(username_or_uid)
        auth = model.UserAuth.get(uid=user)
        return users.check_ident(password, auth.salt, auth.password)
    except model.orm.DoesNotExist:
        return False


def validate_session(token):
    if isinstance(token, str) and token == SESSION_INVALIDATED:
        return None
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token.encode())
    try:
        return model.Session.get(token=token).user
    except model.orm.DoesNotExist:
        return None
