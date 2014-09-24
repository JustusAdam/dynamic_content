from .database_operations import SessionOperations, UserOperations

__author__ = 'justusadam'


# This might not work
_so = None
_uo = None


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
    return s.add_session(uid)


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
    return so().get_user(token)