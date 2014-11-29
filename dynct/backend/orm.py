from peewee import *
from dynct.includes.settings import DATABASE, RUNLEVEL, RunLevel

__author__ = 'justusadam'


def proxy_db():
    if RUNLEVEL == RunLevel.testing:
        return SqliteDatabase(':memory:')
    elif RUNLEVEL == RunLevel.debug:
        return MySQLDatabase(database=DATABASE.name,
                             autocommit=DATABASE.autocommit,
                             user=DATABASE.user,
                             password=DATABASE.password,
                             host=DATABASE.host)


database_proxy = proxy_db()


class BaseModel(Model):
    class Meta:
        database = database_proxy
