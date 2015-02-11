from peewee import *
from framework.includes import inject_settings, log
from framework.util import structures

__author__ = 'Justus Adam'
__version__ = '0.1'


@inject_settings
def proxy_db(settings):
    """
    Return the database specified in settings.

    :return:
    """
    log.print_info('Current RunLevel:  ', settings['runlevel'],  '  ->  ', structures.RunLevel[settings['runlevel']])
    if settings['runlevel'] in [structures.RunLevel.TESTING, structures.RunLevel.DEBUG]:
        db = SqliteDatabase(':memory:')
        db.connect()
        return db
    elif settings['runlevel'] == structures.RunLevel.PRODUCTION:
        if settings['database']['type'] == 'mysql':
            mysqld = MySQLDatabase(
                **{
                    a: b
                    for a, b in settings['database'].keys()
                    if not a == 'type'
                }
            )
            mysqld.connect()
            return mysqld
        elif settings['database']['type'] == 'sqlite':
            sqlited = SqliteDatabase(settings['database']['name'])
            sqlited.connect()
            return sqlited
    else:
        raise ValueError


database_proxy = proxy_db()


class ConnectedModel(Model):
    """Abstract Model with a working database connection"""
    class Meta:
        """Internal class for constructing peewee meta information"""
        database = database_proxy


class BaseModel(ConnectedModel):
    """Abstract base Model with a unified id field."""
    oid = PrimaryKeyField()
