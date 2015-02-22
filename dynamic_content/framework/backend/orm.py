from peewee import *

from framework.includes import SettingsDict
from framework.machinery import component

__author__ = 'Justus Adam'
__version__ = '0.1'


@component.inject(SettingsDict)
def proxy_db(settings):
    """
    Return the database specified in settings.

    :return:
    """
    if settings['database']['type'].lower() == 'mysql':
        mysqld = MySQLDatabase(
            **{
                a: b
                for a, b in settings['database'].keys()
                if not a == 'type'
            }
        )
        mysqld.connect()
        return mysqld
    elif settings['database']['type'].lower() == 'sqlite':
        sqlited = SqliteDatabase(settings['database']['name'])
        sqlited.connect()
        return sqlited


database_proxy = proxy_db()


class ConnectedModel(Model):
    """Abstract Model with a working database connection"""
    class Meta:
        """Internal class for constructing peewee meta information"""
        database = database_proxy


class BaseModel(ConnectedModel):
    """Abstract base Model with a unified id field."""
    oid = PrimaryKeyField()
