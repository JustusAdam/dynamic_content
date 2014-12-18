from . import user_information as uinf, login, admin_actions as actions, controller

__author__ = 'justusadam'

name = 'users'

role = 'user_management'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'


def admin_handler(h_name):
    handlers = {
        'create_user': actions.CreateUser,
        'user_overview': controller.UsersOverview,
        'view_permissions': actions.PermissionOverview,
        'edit_permissions': actions.EditPermissions
    }
    return handlers[h_name]


def common_handler(item_type):
    handlers = {
        login.login_prefix: login.LoginCommonHandler,
        'user_information': uinf.UserInformationCommon
    }
    return handlers[item_type]