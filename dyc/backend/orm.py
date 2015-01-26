from peewee import *
from dyc.includes import settings
from dyc.util import console, structures

__author__ = 'Justus Adam'
__version__ = '0.1'


def proxy_db():
    console.print_info('Current RunLevel:  ', settings.RUNLEVEL,  '  ->  ', settings.RunLevel[settings.RUNLEVEL])
    if settings.RUNLEVEL in [settings.RunLevel.TESTING, settings.RunLevel.DEBUG]:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif settings.RUNLEVEL == settings.RunLevel.PRODUCTION:
        if isinstance(settings.DATABASE, structures.MySQL):
            return MySQLDatabase(
                database=settings.DATABASE.name,
                autocommit=settings.DATABASE.autocommit,
                user=settings.DATABASE.user,
                password=settings.DATABASE.password,
                host=settings.DATABASE.host
                ).connect()
        elif isinstance(settings.DATABASE, structures.SQLite):
            return SqliteDatabase(settings.DC_BASEDIR + '/' + settings.DATABASE.name)
    else:
        raise ValueError


database_proxy = proxy_db()


class ConnectedModel(Model):
    class Meta:
        database = database_proxy


class BaseModel(ConnectedModel):
    oid = PrimaryKeyField()
