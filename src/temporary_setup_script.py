"""
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""

__author__ = 'justusadam'


# add admin menu common

from core import comp

comp.add_commons_config('admin_menu', 'menu', 'admin')
comp.assign_common('admin_menu', 'sidebar_left', 4, 'default_theme')


# Add menu item translations

from modules import internationalization as i18n

source_table = 'menu_items'
language = 'english'

i18n.add_display_name('welcome', source_table, language, 'Welcome')
i18n.add_display_name('testpage', source_table, language, 'XKCD')
i18n.add_display_name('setup', source_table, language, 'Setup')


# Add commons title translations

source_table = 'user_management'

i18n.add_display_name('login', source_table, language, 'User Login')
i18n.add_display_name('user_information', source_table, language, 'Account Information')

source_table = 'admin'

i18n.add_display_name('admin_menu', source_table, language, 'Administration Actions')


# assign the important first permissions

from core.users import users

permissions = [
  [
    users.GUEST_GRP, # unauthorized guests
    ['access login page', 'access content type article', 'access common login']
  ], [
    users.AUTH, # any authorized user
    ['access logout']
  ]
]

for (access_group, permission_list) in permissions:
  for permission in permission_list:
    users.new_permission(permission)
    users.assign_permission(access_group, permission)