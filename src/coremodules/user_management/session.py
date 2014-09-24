from .database_operations import SessionOperations, UserOperations
import binascii

__author__ = 'justusadam'


# This might not work
_so = None
_uo = None

TOKEN_ENCODING = 'ascii'


def so():
    global _so
    if not _so:
        _so = SessionOperations()
    return _so


def uo():
    global _uo
    if not _uo:
        _uo = UserOperations()
    return _uo


def start_session(username, password):
    m = uo()
    s = so()
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
            userid = uo().get_id(userid)
    so().close_session(userid)


def authenticate_user(username, password):
    return uo().authenticate_user(username, password)


def validate_session(token):
    if not isinstance(token, bytes):
        token = binascii.unhexlify(token)
    return so().get_user(token)