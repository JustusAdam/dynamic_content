from . import user_information as uinf, login, admin_actions as actions

__author__ = 'justusadam'

name = 'users'

role = 'user_management'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'


def admin_handler(h_name):
    handlers = {
        'create_user': actions.create_user_form,
        'user_overview': uinf.user_information,
        'view_permissions': actions.permission_overview,
        'edit_permissions': actions.edit_permissions
    }
    return handlers[h_name]


def common_handler(item_type):
    handlers = {
        login.login_prefix: login.LoginCommonHandler,
        'user_information': uinf.UserInformationCommon
    }
    return handlers[item_type]