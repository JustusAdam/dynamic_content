"""
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""

__author__ = 'justusadam'


from modules import comp
from modules.users import users
import core
# add admin menu common

comp.add_commons_config('admin_menu', 'menu', 'admin')
comp.assign_common('admin_menu', 'sidebar_left', 4, 'default_theme')


# Add menu item translations

from modules import i18n as i18n

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

ADMIN_GRP = 5

permissions = [
  [
    users.GUEST_GRP, # unauthorized guests
    ['access login page', 'access content type article', 'access common login']
  ], [
    users.AUTH, # any authorized user
    ['access logout', 'access unpublished content type article']
  ], [
    ADMIN_GRP,
    ['edit user accounts', 'access users overview']
  ]
]

for (access_group, permission_list) in permissions:
  for permission in permission_list:
    users.new_permission(permission)
    users.assign_permission(access_group, permission)

# add some useful aliases

aliases = [
  ('/', '/iris/1'),
  ('/welcome', '/iris/1')
]

for alias, source in aliases:
  core.add_alias(source, alias)