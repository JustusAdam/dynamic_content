import collections

__author__ = 'Justus Adam'
__version__ = '0.1'


def Enumeration(name, levels, start=0):
    return collections.namedtuple(
        name, levels
    )(**{b:a for a,b in enumerate(levels, start=start)})


ServerArguments = collections.namedtuple('ServerArguments', ('host', 'port', 'ssl_port'))
MySQL = collections.namedtuple(
    'MySQL',
    ('type', 'user', 'autocommit', 'password', 'name', 'host'))
SQLite = collections.namedtuple(
    'SQLite',
    ('name', )
)


"""
Backbone datastructure for dynamic_content.

Mainly consists (after instantiation by the application) of two dictionaries:
    context:
        global values accessible to the view/template during the rendering process

    config:
        dynamic store for configuration variables used by middleware,
        handlers, decorators etc.
        allows for dynamic interaction of mostly intermediate/middleware
        software and dynamic configuration.
        (used to be done by model attributes, but this seemed cleaner)

    request:
        information about the current request
        (amongst other things 'client' can be found here)
"""
DynamicContent = collections.namedtuple('DynamicContent',
    ('config', 'context', 'request'))
