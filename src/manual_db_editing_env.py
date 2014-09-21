from core.database import Database
from core.database_operations import Alias, ModuleOperations, ContentHandlers, ContentTypes
from coremodules.iris.database_operations import Pages, Fields
from coremodules.commons_engine.database_operations import MenuOperations, CommonsOperations
from coremodules.theme_engine.database_operations import RegionOperations

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