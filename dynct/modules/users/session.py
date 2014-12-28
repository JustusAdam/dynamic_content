import binascii
from . import model, users
import datetime
import os
import peewee
from dynct.util import time


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
    if isinstance(uid_or_username, int) or uid_or_username.isdigit():
        user = model.User.get(oid=uid_or_username)
    else:
        user = model.User.get(username=uid_or_username)

    try:
        token = model.Session.get(user=user)
        token = token.token
    except peewee.DoesNotExist:
        token = new_token()
        model.Session.create(token=token, user=user, expires=new_exp_time())

    return binascii.hexlify(token).decode()


def close_session(uid_or_username):
    if isinstance(uid_or_username, str):
        if uid_or_username.isdigit() or isinstance(uid_or_username, int):
            uid_or_username = int(uid_or_username)
        else:
            uid_or_username = model.User.get(username=uid_or_username).uid
    model.Session.get(uid=uid_or_username).delete()


def authenticate_user(username_or_uid, password):
    if not isinstance(username_or_uid, int) or username_or_uid.isdigit():
        username_or_uid = model.User.get(username=username_or_uid).oid
    try:
        auth = model.UserAuth.get(uid=int(username_or_uid))
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