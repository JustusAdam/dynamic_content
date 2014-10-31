import binascii

from dynct.modules.users.database_operations import SessionOperations, UserOperations


__author__ = 'justusadam'


def start_session(username, password):
    m = UserOperations()
    s = SessionOperations()
    assert isinstance(m, UserOperations)
    if not authenticate_user(username, password):
        return None
    uid = m.get_uid(username)
    return binascii.hexlify(s.add_session(uid)).decode()


def close_session(uid):
    if isinstance(uid, str):
        if uid.isalpha():
            uid = int(uid)
        else:
            uid = UserOperations().get_uid(uid)
    SessionOperations().close_session(uid)


def authenticate_user(username_or_uid, password):
    ops = UserOperations()
    if not isinstance(username_or_uid, int) or not username_or_uid.isdigit():
        uid = ops.get_uid(username_or_uid)
    else:
        uid = username_or_uid
    return ops.authenticate_user(uid, password)


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    return SessionOperations().get_user(token)