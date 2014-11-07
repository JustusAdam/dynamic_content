import datetime

__author__ = 'justusadam'


def utcnow():
    """
    Returns the current utc time without microseconds to allow matching with mysql.
    :return:
    """
    a = datetime.datetime.utcnow()
    return a - datetime.timedelta(microseconds=a.microsecond)