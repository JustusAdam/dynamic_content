__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from .login import LoginHandler, LoginCommonHandler, LogoutHandler, login_prefix, logout_prefix
from . import user_information

name = 'olymp'

role = 'core'


def load_modules():
    m = Modules()
    m.reload()
    return m


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