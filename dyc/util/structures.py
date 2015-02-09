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
    ('user', 'autocommit', 'password', 'name', 'host'))
SQLite = collections.namedtuple(
    'SQLite',
    ('name', )
)

LoggingLevel = Enumeration(
    'Logging',
    ('LOG_WARNINGS', 'LOG_ERRORS', 'THROW_ERRORS', 'THROW_ALL')
    )
RunLevel = Enumeration(
    'RunLevel',
    ('TESTING', 'DEBUG', 'PRODUCTION')
    )
PathMaps = Enumeration('PathMaps', ('MULTI_TABLE', 'TREE'))
ServerTypes = Enumeration('ServerTypes', ('WSGI', 'PLAIN'))
Distributions = Enumeration(
    'Distributions',
    ('FULL', 'STANDARD', 'FRAMEWORK')
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
    ('config', 'context', 'request', 'handler_options'))



class InvisibleList(list):
    def __init__(self, iterable, render_func=str):
        super().__init__(iterable)
        assert callable(render_func)
        self.render_func = render_func

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __add__(self, other):
        a = InvisibleList(self)
        a.extend(other)
        return a

    def __str__(self):
        return ''.join(self.render_func(a) for a in self)