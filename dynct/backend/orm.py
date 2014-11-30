from peewee import *
from dynct.includes.settings import DATABASE, RUNLEVEL, RunLevel

__author__ = 'justusadam'


def proxy_db():
    if RUNLEVEL == RunLevel.testing:
        return SqliteDatabase(':memory:')
    elif RUNLEVEL == RunLevel.debug:
        return SqliteDatabase('debug.db')
    elif RUNLEVEL == RunLevel.production:
        return MySQLDatabase(database=DATABASE.name,
                             autocommit=DATABASE.autocommit,
                             user=DATABASE.user,
                             password=DATABASE.password,
                             host=DATABASE.host)
    else: raise ValueError


database_proxy = proxy_db()


class BaseModel(Model):
    oid = PrimaryKeyField()
    class Meta:
        database = database_proxy