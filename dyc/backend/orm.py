from peewee import *
from dyc.includes import settings
from dyc.util import console, structures

__author__ = 'Justus Adam'
__version__ = '0.1'


def proxy_db():
    console.print_info('Current RunLevel:  ', settings['runlevel'],  '  ->  ', structures.RunLevel[settings['runlevel']])
    if settings['runlevel'] in [structures.RunLevel.TESTING, structures.RunLevel.DEBUG]:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif settings['runlevel'] == structures.RunLevel.PRODUCTION:
        if settings['database']['type'] == 'mysql':
            return MySQLDatabase(
                **{a:b for a,b in settings['database'].keys() if not a == 'type'}
                ).connect()
        elif settings['database']['type'] == 'sqlite':
            return SqliteDatabase(settings['database']['name'])
    else:
        raise ValueError


database_proxy = proxy_db()


class ConnectedModel(Model):
    class Meta:
        database = database_proxy


class BaseModel(ConnectedModel):
    oid = PrimaryKeyField()
