from .login import LoginHandler
from . import session

__author__ = 'justusadam'


name = 'user_management'

role = 'user_management'

login_prefix = 'login'


def content_handler(url, parent_handler):
    return LoginHandler(url, parent_handler)


def prepare():
    from core.database_operations import ContentHandlers
    from .database_operations import UserOperations, SessionOperations
    cho = ContentHandlers()
    so = SessionOperations()
    uo = UserOperations()
    so.init_tables()
    uo.init_tables()
    cho.add_new('login', 'user_management', login_prefix)