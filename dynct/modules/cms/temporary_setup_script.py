"""
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""

__author__ = 'justusadam'

from dynct.modules import comp
from dynct.modules.users import users
# add admin menu common

admin_menu_common = 'admin_menu'

comp.add_commons_config(admin_menu_common, 'menu', 'admin', True, 1)
comp.assign_common(admin_menu_common, 'sidebar_left', 4, 'default_theme')


# Add menu item translations

from dynct.modules import i18n as i18n

source_table = 'menu_items'
language = 'english'

i18n.add_display_name('welcome', source_table, language, 'Welcome')
i18n.add_display_name('testpage', source_table, language, 'XKCD')
i18n.add_display_name('setup', source_table, language, 'Setup')


# Add commons title translations

source_table = 'user_management'
user_information_common = 'user_information'

i18n.add_display_name('login', source_table, language, 'User Login')
i18n.add_display_name(user_information_common, source_table, language, 'Account Information')

source_table = 'admin'

i18n.add_display_name('admin_menu', source_table, language, 'Administration Actions')


# assign the important first permissions

ADMIN_GRP = 5

permissions = [
    [
        users.GUEST_GRP, 'unauthorized guests',
        ['access login page', 'access content type article', 'access common login']
    ], [
        users.AUTH, 'any authorized user',
        ['access logout', 'access unpublished content type article', 'access content type article',
         'access common ' + user_information_common, 'view own user info']
    ], [
        ADMIN_GRP, 'admin',
        ['edit user accounts', 'access users overview', 'edit content type article', 'add content type article',
         'access common ' + admin_menu_common, 'access admin pages', 'view other user info', 'view permissions',
         'edit permissions']
    ]
]

for (access_group, name, permission_list) in permissions:
    users.add_acc_grp(name, access_group)
    for permission in permission_list:
        users.new_permission(permission)
        users.assign_permission(access_group, permission)

        # add some useful aliases

        # aliases = [
        # ('/', '/iris/1'),
        # ('/welcome', '/iris/1')
        # ]
        #
        # for alias, source in aliases:
        #   core.add_alias(source, alias)