import binascii

from .database_operations import SessionOperations, UserOperations


__author__ = 'justusadam'


def start_session(username, password):
    m = UserOperations()
    s = SessionOperations()
    assert isinstance(m, UserOperations)
    if not authenticate_user(username, password):
        return None
    uid = m.get_id(username)
    return binascii.hexlify(s.add_session(uid)).decode()


def close_session(userid):
    """
    function also accepts username
    :param userid:
    :return:
    """
    if isinstance(userid, str):
        if userid.isalpha():
            userid = int(userid)
        else:
            userid = UserOperations().get_id(userid)
    SessionOperations().close_session(userid)


def authenticate_user(username, password):
    return UserOperations().authenticate_user(username, password)


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    return SessionOperations().get_user(token)