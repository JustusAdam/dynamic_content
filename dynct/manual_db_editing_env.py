from dynct.modules.admin.database_operations import AdminOperations
from dynct.backend.database import Database
from dynct.core.database_operations import Alias, ModuleOperations, ContentHandlers, ContentTypes
from dynct.modules.iris.database_operations import Pages, Fields
from dynct.modules.commons.database_operations import MenuOperations, CommonsOperations
from dynct.modules.comp.database_operations import RegionOperations
from dynct.modules.users.database_operations import UserOperations, SessionOperations, AccessOperations

__author__ = 'justusadam'

info = []
print('For information on editing objects use print(info)')

db = Database()
info.append('Database: db')

al_dbo = Alias()
info.append('Alias editing Object: al_dbo')

mo_dbo = ModuleOperations()
info.append('Modules editing object: mo_dbo')

ch_dbo = ContentHandlers()
info.append('Content handlers editing object: ch_dbo')

ct_dbo = ContentTypes()
info.append('Content types editing object: ct_dbo')

fi_dbo = Fields()
info.append('Fields editing object: fi_dbo')

pa_dbo = Pages()
info.append('Pages editing object: pa_dbo')

men_dbo = MenuOperations()
info.append('Menu editing object: men_dbo')

ro_dbo = RegionOperations()
info.append('Region editing object: ro_dbo')

com_dbo = CommonsOperations()
info.append('Commons editing object: com_dbo')

us_dbo = UserOperations()
info.append('User operations: us_dbo')

ses_dbo = SessionOperations()
info.append('Session Operations: ses_dbo')

ac_dbo = AccessOperations()
info.append('Access Operations: ac_dbo')

ad_dbo = AdminOperations()
info.append('Admin Pages Operations: ad_dbo')