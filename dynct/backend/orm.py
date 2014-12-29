from peewee import *
from dynct.includes import settings

__author__ = 'justusadam'


def proxy_db():
    print(settings.RUNLEVEL)
    if settings.RUNLEVEL == settings.RunLevel.testing:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif settings.RUNLEVEL == settings.RunLevel.debug:
        return SqliteDatabase('debug.db').connect()
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