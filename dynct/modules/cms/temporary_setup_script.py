"""
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""
from dynct.core.model import ContentHandler, ContentTypes
from dynct.modules.commons.model import MenuItem, Common
from dynct.modules.comp import add_commons_config, assign_common
from dynct.modules.iris.model import FieldConfig, Page, field

__author__ = 'justusadam'

from dynct.modules import comp, admin
from dynct.modules.users import users
from dynct import core

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

aliases = [
('/', '/iris/1'),
('/welcome', '/iris/1')
]

for alias, source in aliases:
  core.add_alias(source, alias)

# from admin.prepare()

ContentHandler('admin', 'admin', 'admin').save()

# from commons.prepare()

for name, path, menu, enabled, parent, weight in [
                                                    ('welcome', '/iris/1', 'start_menu', True, '<root>', 1),
                                                    ('welcome', '/iris/1', 'start_menu', True, '<root>', 1),
                                                    ('testpage', '/iris/2', 'start_menu', True, '<root>', 2),
                                                    ('setup', '/setup', 'start_menu', True, 'welcome', 1)
                                                ]:
    MenuItem.create(
        display_name=name,
        path=path,
        menu=menu,
        enabled=enabled,
        parent=parent,
        weight=weight
    )

for name, content in [('copyright', '<p>\"dynamic_content\" CMS - © Justus Adam 2014</p>')]:
    Common.create(
        machine_name=name,
        content=content
    )

# from comp.prepare()

for machine_name, type_, handler, access_type in [
    ('start_menu', 'menu', 'commons', 0),
    ('copyright', 'com_text', 'commons', 0)
]:
    add_commons_config()

add_commons_config('start_menu', 'menu', 'commons', False, 0)
assign_common('start_menu', 'navigation', 1, 'default_theme')
assign_common('copyright', 'footer', 1, 'default_theme')
add_commons_config('copyright', 'com_text', 'commons', False, 0)

# from iris.prepare()

name = 'iris'

role = 'page_handler'

path_prefix = 'iris'

ContentHandler('iris', name, path_prefix).save()
ContentTypes('article', 'Simple Article', 'iris', 'active').save()
FieldConfig('body', 'Body', 'article', 'iris', 1, '')

# add admin pages

# add some initial pages


p = page('iris')('article', "Welcome to \"dynamic_content\"", 1, True)
p.save()
page_id = p.get_id()
field('body')(page_id=page_id, path_prefix='iris',
            content='<div><h3>Welcome to your \"dynamic_content\" installation</h3><p>First off, thank you for choosing this software to run your website</p><p>I try to make this software to be the easiest to use and extend content management software there is.</p><div>I hope you\'ll enjoy using this software. If you are a developer please consider helping out with the development, I am always looking for aid and fresh ideas.</div></div><image src=\"http://imgs.xkcd.com/comics/server_attention_span.png\" width=\"550px\" style=\"padding:20px 0px\">').save()

p = page('iris')('article', 'Wuhuuu', 1, True)
p.save()
page_id = p.get_id()
field('body')(page_id,
            '<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>', 'iris').save()

# from users.prepare()

from dynct.modules.users import login_prefix, logout_prefix, START_REGION, START_THEME

# add login page
core.add_content_handler('login', name, login_prefix)
core.add_content_handler('logout', name, logout_prefix)
core.add_content_handler('users', name, 'users')

# add login common
comp.add_commons_config('login', 'login', name, True, 1)
comp.add_commons_config('login', START_REGION, 0, START_THEME)
i18n.add_item('login', 'user_management', ('english', 'User Login'))

# add user information common
comp.add_commons_config('user_information', 'user_information', name, True, 1)
comp.assign_common('user_information', START_REGION, 1, START_THEME)
i18n.add_item('user_information', 'user_management', ('english', 'Your Account Information'))

# add admin pages
admin.new_category('user', 'Users')

admin.new_subcategory('user_management', 'Add and Edit Users', 'user')
admin.new_page('create_user', 'Register new User', 'user_management', name)
admin.new_page('user_overview', 'Overview', 'user_management', name)

admin.new_subcategory('permission_management', 'View and edit Permissions', 'user', 5)
admin.new_page('view_permissions', 'View Permissions', 'permission_management', name)
admin.new_page('edit_permissions', 'Edit Permissions', 'permission_management', name)