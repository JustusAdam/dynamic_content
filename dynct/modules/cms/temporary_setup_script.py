"""
This is a temporary script that will execute some queries on the database to fill in the necessary content
to get some basic site setup done. It will be done in this script to avoid trying to insert into tables that have not
been created yet.
"""
__author__ = 'justusadam'


def init_tables():
    from dynct.includes import log
    from importlib import import_module
    from dynct.backend.orm import BaseModel
    from dynct.core import Modules
    import inspect

    for module_name, module in Modules.items():
        try:
            m = import_module('.model', module.__name__)
            for item in m.__dict__.values():
                if inspect.isclass(item) and issubclass(item, BaseModel):
                    try:
                        item.create_table()
                    except Exception as e:
                        print(e)
                        log.write_error(function='create_table', message=str(e))
        except Exception as error:
            print(error)
            log.write_error(function='init_tables', message=str(error))


def initialize():
    from dynct.core.model import ContentHandler, ContentTypes

    from dynct.modules.commons.model import MenuItem, Common
    from dynct.modules.comp import add_commons_config, assign_common
    from dynct.modules.iris.model import FieldConfig, Page, field

    from dynct.modules import admin
    from dynct.modules.users import users
    from dynct import core
    from dynct.modules.users import START_REGION, START_THEME


    admin_menu_common = 'admin_menu'


    # assign the important first permissions

    ADMIN_GRP = 5

    from dynct.modules.users.model import AccessGroup

    for item in AccessGroup.select():
        print(item.oid, item.machine_name)

    print(AccessGroup._meta.database.database)

    users.add_acc_grp('control_group', users.CONTROL_GROUP)

    permissions = [
        [
            users.GUEST_GRP, 'unauthorized guests',
            ['access login page', 'access content type article', 'access common login']
        ], [
            users.AUTH, 'any authorized user',
            ['access logout', 'access unpublished content type article', 'access content type article',
             'access common ' + 'user_information', 'view own user info']
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



    ContentHandler.create(machine_name='admin', path_prefix='admin', handler_module='admin')



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



    for machine_name, type_, handler, show_title, access_type in [
        # commons from comp
        ('start_menu', 'menu', 'commons', False, 0),
        ('copyright', 'com_text', 'commons', False, 0),
        # commons from users
        ('login', 'login', 'users', True, 1), # login common
        ('user_information', 'user_information', 'users', True, 1), # user information common
        # from admin
        (admin_menu_common, 'menu', 'admin', True, 1)
    ]:
        add_commons_config(machine_name=machine_name,
                           commons_type=type_,
                           handler_module=handler,
                           show_title=show_title,
                           access_type=access_type)

    for name, region, weight, theme in [
        # from comp
        ('start_menu', 'navigation', 1, 'default_theme'),
        ('copyright', 'footer', 1, 'default_theme'),
        # from users
        ('login', START_REGION, 0, START_THEME),
        ('user_information', START_REGION, 1, START_THEME),
        # from admin
        (admin_menu_common, 'sidebar_left', 4, 'default_theme')
    ]:
        assign_common(common_name=name,
                      region=region,
                      weight=weight,
                      theme=theme)


    name = 'iris'

    path_prefix = 'iris'

    ContentHandler.create(machine_name='iris',
                          module=name,
                          path_prefix=path_prefix)
    ContentTypes.create(machine_name='article',
                        displey_name='Simple Article',
                        content_handler='iris',
                        theme='active')
    FieldConfig.create(machine_name='body',
                       display_name='Body',
                       content_type='article',
                       handler_module='iris',
                       weight=1)

    # add some initial pages


    p = Page.create(content_type='article', title="Welcome to \"dynamic_content\"", creator=1, published=True)
    page_id = p.oid
    field('body').create(page_id=page_id, path_prefix='iris',
                content='<div><h3>Welcome to your \"dynamic_content\" installation</h3><p>First off, thank you for choosing this software to run your website</p><p>I try to make this software to be the easiest to use and extend content management software there is.</p><div>I hope you\'ll enjoy using this software. If you are a developer please consider helping out with the development, I am always looking for aid and fresh ideas.</div></div><image src=\"http://imgs.xkcd.com/comics/server_attention_span.png\" width=\"550px\" style=\"padding:20px 0px\">')

    p = Page.create(content_type='article', title='Wuhuuu', creator=1, published=True)
    page_id = p.oid
    field('body').create(page_id=page_id,
                content='<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>', path_prefix='iris')

    # add admin pages

    for name, display_name in [
        ('user', 'Users')
    ]:
        admin.new_category(machine_name=name,
                           display_name=display_name)

    for machine_name, display_name, category in [
        ('user_management', 'Add and Edit Users', 'user'),
        ('permission_management', 'View and edit Permissions', 'user', 5)
    ]:
        admin.new_subcategory(machine_name=machine_name,
                              display_name=display_name,
                              category=category)

    for machine_name, display_name, subcategory, handler in [
        ('create_user', 'Register new User', 'user_management', name),
        ('user_overview', 'Overview', 'user_management', name),
        ('view_permissions', 'View Permissions', 'permission_management', name),
        ('edit_permissions', 'Edit Permissions', 'permission_management', name)
    ]:
        admin.new_page(machine_name=machine_name,
                       display_name=display_name,
                       subcategory=subcategory,
                       handler_module=handler)


