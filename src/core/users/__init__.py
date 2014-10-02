from .login import LoginHandler, LoginCommonHandler, LogoutHandler, login_prefix, logout_prefix
from . import session, users
from .user_information import UserInformationCommon
from .admin_actions import CreateUser

__author__ = 'justusadam'

name = 'users'

role = 'user_management'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'


def admin_handler(name):
  handlers = {
    'create_user': CreateUser
  }
  return handlers[name]


def content_handler(url):
  handlers = {
    login_prefix: LoginHandler,
    logout_prefix: LogoutHandler
  }
  return handlers[url.page_type]


def common_handler(item_type, item_name, show_title, user, access_group):
  handlers = {
    login_prefix: LoginCommonHandler,
    'user_information': user_information.UserInformationCommon
  }
  return handlers[item_type](item_name, show_title, user, access_group)


def form_handler():
  pass


def prepare():
  import core
  from .database_operations import UserOperations, SessionOperations
  from core.comp.database_operations import RegionOperations
  # from coremodules.internationalization.database_operations import DisplayNamesOperations
  so = SessionOperations()
  uo = UserOperations()
  ro = RegionOperations()
  # dn = DisplayNamesOperations()
  so.init_tables()
  uo.init_tables()

  # add login page
  core.add_content_handler('login', 'users', login_prefix)
  core.add_content_handler('logout', 'users', logout_prefix)

  # add login common
  ro.add_item('login', START_REGION, 0, START_THEME)
  ro.add_item_conf('login', 'login', 'users', True)
  #dn.add_item('login', 'user_management', ('english', 'User Login'))

  # add user information common
  ro.add_item_conf('user_information', 'user_information', 'users', True)
  ro.add_item('user_information', START_REGION, 1, START_THEME)
  #dn.add_item('user_information', 'user_management', ('english', 'Your Account Information'))