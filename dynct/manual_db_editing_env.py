from dynct.backend.database import Database
from dynct.core.database_operations import Alias, ModuleOperations, ContentHandlers, ContentTypes

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
