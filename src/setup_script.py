from core import database_operations as dbo
from coremodules.theme_engine.database_operations import RegionOperations
from coremodules.internationalization.database_operations import DisplayNamesOperations
from core import login

__author__ = 'justusadam'

START_REGION = 'sidebar_left'

START_THEME = 'default_theme'

cho = dbo.ContentHandlers()
so = dbo.SessionOperations()
uo = dbo.UserOperations()
ro = RegionOperations()
dn = DisplayNamesOperations()
al = dbo.Alias()
mo = dbo.ModuleOperations()

cho.init_tables()
so.init_tables()
uo.init_tables()
al.init_tables()
mo.init_tables()

# add login page
cho.add_new('login', 'user_management', login.login_prefix)
cho.add_new('logout', 'user_management', login.logout_prefix)

# add login common
ro.add_item('login', START_REGION, 0, START_THEME)
ro.add_item_conf('login', 'login', 'user_management', True)
dn.add_item('login', 'user_management', ('english', 'User Login'))

# add user information common
ro.add_item_conf('user_information', 'user_information', 'user_management', True)
ro.add_item('user_information', START_REGION, 1, START_THEME)
dn.add_item('user_information', 'user_management', ('english', 'Your Account Information'))

al.add_alias('/iris/1', '/welcome')