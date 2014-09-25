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
    from coremodules.theme_engine.database_operations import RegionOperations
    from coremodules.internationalization.database_operations import DisplayNamesOperations
    cho = ContentHandlers()
    so = SessionOperations()
    uo = UserOperations()
    ro = RegionOperations()
    dn = DisplayNamesOperations()
    so.init_tables()
    uo.init_tables()

    cho.add_new('login', 'user_management', login_prefix)
    ro.add_item('login', 'sidebar_left', 0, 'default_theme')
    ro.add_item_conf('login', 'login', 'user_management')
    dn.add_item('login', 'login', {'english': 'User Login'})