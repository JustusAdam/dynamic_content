from .login import LoginHandler, LoginCommonHandler, LogoutHandler, login_prefix, logout_prefix
from modules import admin
from . import users, session
from .admin_actions import CreateUser, UsersOverview, factory, PermissionOverview, EditPermissions
from . import user_information

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


def content_handler(url):
    handlers = {
        login_prefix: LoginHandler,
        logout_prefix: LogoutHandler,
        'users': factory(url)
    }
    return handlers[url.page_type]


def common_handler(item_type):
    handlers = {
        login_prefix: LoginCommonHandler,
        'user_information': user_information.UserInformationCommon
    }
    return handlers[item_type]


def prepare():
    import core
    from .database_operations import UserOperations, SessionOperations, AccessOperations
    from modules.comp.database_operations import RegionOperations

    # from coremodules.i18n.database_operations import DisplayNamesOperations
    so = SessionOperations()
    uo = UserOperations()
    ro = RegionOperations()
    aa = AccessOperations()
    # dn = DisplayNamesOperations()
    so.init_tables()
    uo.init_tables()
    aa.init_tables()

    # add login page
    core.add_content_handler('login', name, login_prefix)
    core.add_content_handler('logout', name, logout_prefix)
    core.add_content_handler('users', name, 'users')

    # add login common
    ro.add_item_conf('login', 'login', name, True, 1)
    ro.add_item('login', START_REGION, 0, START_THEME)
    # dn.add_item('login', 'user_management', ('english', 'User Login'))

    # add user information common
    ro.add_item_conf('user_information', 'user_information', name, True, 1)
    ro.add_item('user_information', START_REGION, 1, START_THEME)
    #dn.add_item('user_information', 'user_management', ('english', 'Your Account Information'))

    # add admin pages
    admin.new_category('user', 'Users')

    admin.new_subcategory('user_management', 'Add and Edit Users', 'user')
    admin.new_page('create_user', 'Register new User', 'user_management', name)
    admin.new_page('user_overview', 'Overview', 'user_management', name)

    admin.new_subcategory('permission_management', 'View and edit Permissions', 'user', 5)
    admin.new_page('view_permissions', 'View Permissions', 'permission_management', name)
    admin.new_page('edit_permissions', 'Edit Permissions', 'permission_management', name)
    #admin.new_page('delete_user', 'Remove a User Account', 'user_management', name)