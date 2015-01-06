import collections

__author__ = 'Justus Adam'
__version__ = '0.1'


def EnumLevel(name, levels, start=0):
    return collections.namedtuple(
        name, levels
    )(**{b:a for a,b in enumerate(levels, start=start)})


ServerArguments = collections.namedtuple('ServerArguments', ('host', 'port'))
DatabaseArguments = collections.namedtuple(
    'database',
    ('type', 'user', 'autocommit', 'password', 'name', 'host'))
