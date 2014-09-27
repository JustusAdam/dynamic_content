from .login import LoginHandler, LoginCommonHandler, LogoutHandler, login_prefix, logout_prefix
from . import session, users
from .user_information import UserInformationCommon

__author__ = 'justusadam'

name = 'user_management'

role = 'user_management'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'


def content_handler(url, parent_handler):
  handlers = {
    login_prefix: LoginHandler,
    logout_prefix: LogoutHandler
  }
  return handlers[url.page_type](url, parent_handler)


def common_handler(item_type, item_name, show_title, user, access_group):
  handlers = {
    login_prefix: LoginCommonHandler,
    'user_information': user_information.UserInformationCommon
  }
  return handlers[item_type](item_name, show_title, user, access_group)


def prepare():
  from core.database_operations import ContentHandlers
  from .database_operations import UserOperations, SessionOperations
  from coremodules.theme_engine.database_operations import RegionOperations
  # from coremodules.internationalization.database_operations import DisplayNamesOperations
  cho = ContentHandlers()
  so = SessionOperations()
  uo = UserOperations()
  ro = RegionOperations()
  # dn = DisplayNamesOperations()
  so.init_tables()
  uo.init_tables()

  # add login page
  cho.add_new('login', 'user_management', login_prefix)
  cho.add_new('logout', 'user_management', logout_prefix)

  # add login common
  ro.add_item('login', START_REGION, 0, START_THEME)
  ro.add_item_conf('login', 'login', 'user_management', True)
  #dn.add_item('login', 'user_management', ('english', 'User Login'))

  # add user information common
  ro.add_item_conf('user_information', 'user_information', 'user_management', True)
  ro.add_item('user_information', START_REGION, 1, START_THEME)
  #dn.add_item('user_information', 'user_management', ('english', 'Your Account Information'))