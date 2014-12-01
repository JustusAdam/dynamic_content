from peewee import *
from dynct.includes.settings import DATABASE, RUNLEVEL, RunLevel

__author__ = 'justusadam'


def proxy_db():
    print(RUNLEVEL)
    if RUNLEVEL == RunLevel.testing:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif RUNLEVEL == RunLevel.debug:
        return SqliteDatabase('debug.db').connect()
    elif RUNLEVEL == RunLevel.production:
        return MySQLDatabase(database=DATABASE.name,
                             autocommit=DATABASE.autocommit,
                             user=DATABASE.user,
                             password=DATABASE.password,
                             host=DATABASE.host).connect()
    else: raise ValueError


database_proxy = proxy_db()


class BaseModel(Model):
    oid = PrimaryKeyField()
    class Meta:
        database = database_proxy