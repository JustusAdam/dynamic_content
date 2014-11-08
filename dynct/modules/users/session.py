import binascii
from . import ar
import datetime
import os
from dynct.util.time import utcnow


__author__ = 'justusadam'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
SESS_TOKEN_LENGTH = 16


def new_token():
    return os.urandom(SESS_TOKEN_LENGTH)


def new_exp_time():
    return utcnow() - datetime.timedelta(seconds=SESSION_LENGTH)


def start_session(uid_or_username:str, password):
    if not authenticate_user(uid_or_username, password):
        return None
    if isinstance(uid_or_username, int) or uid_or_username.isdigit():
        uid = uid_or_username
    else:
        uid = ar.User.get(username=uid_or_username).uid
    token = ar.Session.get(uid=uid)
    if not token:
        token = new_token()
        ar.Session(token, uid, new_exp_time()).save()
    else:
        token = token.sess_token
    return binascii.hexlify(token).decode()


def close_session(uid_or_username):
    if isinstance(uid_or_username, str):
        if uid_or_username.isdigit() or isinstance(uid_or_username, int):
            uid_or_username = int(uid_or_username)
        else:
            uid_or_username = ar.User.get(username=uid_or_username).uid
    ar.Session.get(uid=uid_or_username).delete()


def authenticate_user(username_or_uid, password):
    if not isinstance(username_or_uid, int) or username_or_uid.isdigit():
        username_or_uid = ar.User.get(username=username_or_uid).uid
    return bool(ar.UserAuth.get(username=username_or_uid, password=password))


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    return ar.Session.get(sess_token=token).uid