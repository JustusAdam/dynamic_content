from .user_information import UsersOverview
from .login import LoginCommonHandler, login_prefix, logout_prefix
from .admin_actions import CreateUser, factory, PermissionOverview, EditPermissions
from . import user_information
from .controller import UserController

__author__ = 'justusadam'

name = 'users'

role = 'user_management'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'


def admin_handler(h_name):
    handlers = {
        'create_user': CreateUser,
        'user_overview': UsersOverview,
        'view_permissions': PermissionOverview,
        'edit_permissions': EditPermissions
    }
    return handlers[h_name]


def common_handler(item_type):
    handlers = {
        login_prefix: LoginCommonHandler,
        'user_information': user_information.UserInformationCommon
    }
    return handlers[item_type]