import binascii
from . import model
import datetime
import os
from dynct.util.time import utcnow
from .users import check_ident


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
        uid = model.User.get(username=uid_or_username).uid
    token = model.Session.get(uid=uid)
    if not token:
        token = new_token()
        model.Session(token, uid, new_exp_time()).save()
    else:
        token = token.sess_token
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
    auth = model.UserAuth.get(uid=username_or_uid)
    if not auth:
        return False
    return check_ident(password, auth.salt, auth.password)


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    x = model.Session.get(sess_token=token)
    if x:
        return x.uid
    else:
        return None