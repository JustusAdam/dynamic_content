from peewee import *
from dyc.includes import settings
from dyc.util import console

__author__ = 'Justus Adam'


def proxy_db():
    console.cprint('Current RunLevel:  ', settings.RUNLEVEL,  '  ->  ', settings.RunLevel[settings.RUNLEVEL])
    if settings.RUNLEVEL in [settings.RunLevel.testing, settings.RunLevel.debug]:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif settings.RUNLEVEL == settings.RunLevel.production:
        return MySQLDatabase(database=settings.DATABASE.name,
                             autocommit=settings.DATABASE.autocommit,
                             user=settings.DATABASE.user,
                             password=settings.DATABASE.password,
                             host=settings.DATABASE.host).connect()
    else:
        raise ValueError


database_proxy = proxy_db()


class BaseModel(Model):
    oid = PrimaryKeyField()

    class Meta:
        database = database_proxy