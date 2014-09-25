from .login import LoginHandler, LoginCommonHandler
from . import session, users

__author__ = 'justusadam'


name = 'user_management'

role = 'user_management'

login_prefix = 'login'


def content_handler(url, parent_handler):
    return LoginHandler(url, parent_handler)


def common_handler(item_type, item_name, show_title):
    handlers = {
        'login': LoginCommonHandler
    }
    return handlers[item_type](item_name, show_title)


def prepare():
    from core.database_operations import ContentHandlers
    from .database_operations import UserOperations, SessionOperations
    cho = ContentHandlers()
    so = SessionOperations()
    uo = UserOperations()
    so.init_tables()
    uo.init_tables()
    cho.add_new('login', 'user_management', login_prefix)