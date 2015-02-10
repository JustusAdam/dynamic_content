import pathlib

__doc__ = """
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""
from framework.util import console, structures
from framework.includes import inject_settings


__author__ = 'Justus Adam'
__version__ = '0.2.1'


@inject_settings
def init_tables(settings):
    from framework.includes import log
    from importlib import import_module
    from framework.backend import orm
    import inspect


    def _init_module(m):
        for item in dir(m):
            item = getattr(m, item)
            if inspect.isclass(item) and issubclass(item, orm.Model):
                try:
                    item.create_table()
                    # console.cprint('creating table ' + str(item._meta.db_table))
                except Exception as e:
                    console.print_error(e)
                    log.write_error('create_table:', e)

    c = {}

    for module in settings['modules']:
        c[module] = import_module('dycm.' + module)

    for module in c.values():
        _init_module(module)
        try:
            m = import_module('.model', module.__name__)
            _init_module(m)
        except Exception as error:
            console.print_error(error)
            log.write_error('init_tables:', error)

    from framework.middleware import alias, csrf
    alias.Alias.create_table()
    csrf.ARToken.create_table()


@inject_settings
def initialize(settings):
    from dycm import users as user_module, commons, theming, node

    admin_menu_common = 'admin_menu'

    # assign the important first permissions

    ADMIN_GRP = 5

    user_module.users.add_acc_grp('control_group', user_module.users.CONTROL_GROUP)

    permissions = [
        [
            user_module.users.GUEST_GRP, 'unauthorized guests',
            ['access login page', 'access content type article', 'access common login', 'access node overview']
        ], [
            user_module.users.AUTH, 'any authorized user',
            ['access logout', 'access unpublished content type article', 'access content type article',
             'access common ' + 'user_information', 'view own user info', 'access node overview']
        ], [
            ADMIN_GRP, 'admin',
            ['edit user accounts', 'access users overview', 'edit content type article', 'add content type article',
             'access common ' + admin_menu_common, 'access admin pages', 'view other user info', 'view permissions',
             'edit permissions', 'access node overview']
        ]
    ]

    for access_group, name, permission_list in permissions:
        user_module.users.add_acc_grp(name, access_group)
        for permission in permission_list:
            user_module.users.new_permission(permission)
            user_module.users.assign_permission(access_group, permission)

    if settings['runlevel'] in [structures.RunLevel.TESTING, structures.RunLevel.DEBUG]:
        user_module.users.add_user(username='justus', password='???', email='justus.jonas@verizon.com', first_name='Justus', last_name='Jonas')
        user_module.users.assign_access_group('justus', ADMIN_GRP)
        user_module.users.add_user(username='peter', password='???', email='peter.shaw@verizon.com', first_name='Peter', last_name='Shaw')
        user_module.users.add_user(username='bob', password='???', email='bob.andrews@verizon.com', first_name='Bob', last_name='Andrews')


    # add some useful aliases

    from framework.middleware import alias

    aliases = [
        ('/', '/node/1'),
        ('/welcome', '/node/1')
    ]

    for a, source in aliases:
        alias.add_alias(source, a)



    # add themes

    theme_path = pathlib.Path(theming.__file__).parent

    for name, path, enabled in [
        ('default_theme', str(theme_path / 'themes/default_theme'), True),
        ('admin_theme', str(theme_path / 'themes/admin_theme'), True)
    ]:
        theming.model.Theme.create(
            machine_name=name,
            path=path,
            enabled=enabled
            )

    for machine_name, enabled, children in (
        ('start_menu', True,
         (
             ('<root>', '', True, None, 1),
             ('welcome', '/node/1', True, '<root>', 1),
             ('testpage', '/node/2', True, '<root>', 2),
             ('setup', '/setup', True, 'welcome', 1)
         )
        ),

    ):
        menu = commons.model.Menu.create(
            machine_name=machine_name,
            enabled=enabled)

        for name, path, child_enabled, parent, weight in children:
            commons.model.MenuItem.create(
                display_name=name,
                path=path,
                menu=menu,
                enabled=child_enabled,
                parent=commons.model.MenuItem.get(display_name=parent) if parent else None,
                weight=weight
            )

    for name, content in (('copyright', '<p>\"dynamic_content\" CMS - © Justus Adam 2015</p>'), ):
        commons.model.CommonData.create(
            machine_name=name,
            content=content
        )

    commons_config_list = [
        # commons from comp
        ('start_menu', 'menu', 'commons', 0),
        ('copyright', 'com_text', 'commons', 0),
        # commons from users
        # from admin
        #(admin_menu_common, 'admin_menu', 'admin', 1)
    ]

    commons_list = [
        # from comp
        ('start_menu', 'navigation', 1, 'default_theme', False),
        ('copyright', 'footer', 1, 'default_theme', False),
        # from users

        # from admin
        #(admin_menu_common, 'sidebar_left', 4, 'default_theme', True)
    ]

    if 'user_management' in settings['modules']:
        commons_config_list.extend(
            (
                ('login', 'login', 'users', 1),  # login common
                ('user_information', 'user_information', 'users', 1),  # user information common
            )
        )
        commons_list.extend(
            (
                ('login', user_module.START_REGION, 0, user_module.START_THEME, True),
                ('user_information', user_module.START_REGION, 1, user_module.START_THEME, True),
            )
        )

    for machine_name, type_, handler, access_type in commons_config_list:
        commons.add_commons_config(machine_name=machine_name,
                           commons_type=type_,
                           access_type=access_type)

    for name, region, weight, theme, show_title in commons_list:
        commons.assign_common(common_name=name,
                      region=region,
                      weight=weight,
                      theme=theme,
                      show_title=show_title)


    _ct1 = node.model.ContentType.create(machine_name='article',
                                         displey_name='Simple Article',
                                         theme=theming.model.Theme.get(machine_name='default_theme'))

    bodytype = node.model.FieldType.create(machine_name='body', handler='node.text_field_handler')

    node.model.FieldConfig.create(
        field_type=bodytype,
        content_type=_ct1,
        weight=1)

    # add some initial pages

    bodyfield = node.model.field('body')
    bodyfield.create_table()

    page = node.model.Page.create(content_type=_ct1, page_title="Welcome to \"dynamic_content\"", creator=1,
                                  published=True)
    bodyfield.create(page_id=page.oid, page_type='node',
                     content='<div><h3>Welcome to your \"dynamic_content\" installation</h3><p>First off, thank you for choosing this software to run your website</p><p>I try to make this software to be the easiest to use and extend content management software there is.</p><div>I hope you\'ll enjoy using this software. If you are a developer please consider helping out with the development, I am always looking for aid and fresh ideas.</div></div>')

    page = node.model.Page.create(content_type=_ct1, page_title='Wuhuuu', creator=1, published=True)
    bodyfield.create(page_id=page.oid,
                     content='<p>More content is good</p>',
                     page_type='node')

    # add admin pages
    #
    # categories = {}
    #
    # subcategories = {}
    #
    # for name, display_name in [
    #     ('user', 'Users')
    # ]:
    #     categories[name] = admin.new_category(machine_name=name,
    #                                           display_name=display_name)
    #
    # for machine_name, display_name, category in [
    #     ('user_management', 'Add and Edit Users', 'user'),
    #     ('permission_management', 'View and edit Permissions', 'user')
    # ]:
    #     subcategories[machine_name] = admin.new_subcategory(machine_name=machine_name,
    #                                                         display_name=display_name,
    #                                                         category=categories[category])
    #
    # name = 'users'
    #
    # for machine_name, display_name, subcategory, handler in [
    #     ('create_user', 'Register new User', 'user_management', name),
    #     ('user_overview', 'Overview', 'user_management', name),
    #     ('view_permissions', 'View Permissions', 'permission_management', name),
    #     ('edit_permissions', 'Edit Permissions', 'permission_management', name)
    # ]:
    #     admin.new_page(machine_name=machine_name,
    #                    display_name=display_name,
    #                    subcategory=subcategories[subcategory])
