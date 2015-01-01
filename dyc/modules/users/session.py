import binascii
from . import model, users
import datetime
import os
import peewee
from dyc.util import time


__author__ = 'justusadam'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
SESS_TOKEN_LENGTH = 16


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
    except peewee.DoesNotExist:
        token = new_token()
        model.Session.create(token=token, user=user, expires=new_exp_time())

    return binascii.hexlify(token).decode()


def close_session(uid_or_username):
    user = users.get_single_user(uid_or_username)
    model.Session.get(user=user).delete()


def authenticate_user(username_or_uid, password):
    user = users.get_single_user(username_or_uid)
    try:
        auth = model.UserAuth.get(uid=user)
        return users.check_ident(password, auth.salt, auth.password)
    except peewee.DoesNotExist:
        return False


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    try:
        return model.Session.get(token=token).user
    except peewee.DoesNotExist:
        return None