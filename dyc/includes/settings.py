"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make dynamic_content functional.

Might need to be expanded.
"""
from collections import namedtuple
from pathlib import Path

__author__ = 'justusadam'


class EnumLevel(object):
    def __init__(self, *levels):
        if len(levels) == 1 and not isinstance(levels[0], str) and hasattr(levels[0], '__iter__'):
            levels = levels[0]
        self.levels = levels

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.levels[item]
        elif item in self.levels:
            return self.levels.index(item)
        elif item.lower() in self.levels:
            return self.levels.index(item)
        raise KeyError

    def __repr__(self):
        return '\n'.join(repr(item) for item in zip(range(len(self.levels)), self.levels))


LoggingLevel = EnumLevel(*['log_warnings', 'log_errors', 'throw_errors', 'throw_all'])
RunLevel = EnumLevel(*['testing', 'debug', 'production'])
PathMaps = {
    'multitable',
    'tree'
}


# the order in this list dictates the order in which these modules will be activated
DEFAULT_MODULES = [
    'form', 'admin', 'comp', 'users', 'commons', 'file',
    'iris',
    'i18n'
]
FILE_DIRECTORIES = {
    'theme': [
        'custom/themes',
        'themes'
    ],
    'private': 'custom/files/private',
    'public': 'custom/files/public'
}
MODULES_DIRECTORIES = ['custom/modules', 'modules']
NECESSARY_MODULE_ATTRIBUTES = [
    'name',
    'role'
]
COREMODULES_DIRECTORIES = ['core']
MODULE_CONFIG_NAME = 'config.json'
ALLOW_HIDDEN_FILES = False
# Setting the above option to true will allow access to files starting with a '.' via the file handler/url
# it is highly recommended to NOT set this flag to true!
ALLOW_INDEXING = True
BROWSER_CACHING = False
HASHING_ALGORITHM = 'sha256'
HASHING_ROUNDS = 100000
HASH_LENGTH = 64
SALT_LENGTH = 16
DEFAULT_THEME = 'default_theme'
DEFAULT_ADMIN_THEME = 'admin_theme'
LOGGING_LEVEL = LoggingLevel.throw_all
SERVER = namedtuple('server', ['host', 'port'])(port=9012, host='localhost')
DATABASE = (namedtuple('database',
                       ['type', 'user', 'autocommit', 'password', 'name', 'host'])
            ('mysql', 'python_cms', True, 'python_cms', 'python_cms', 'localhost'))
BASEDIR = str(Path(__file__).parent.resolve())
RUNLEVEL = RunLevel.testing
I18N_SUPPORT_ENABLED = False
SUPPORTED_LANGUAGES = {
    'en_us': 'english (us)',
    'en_gb': 'english (gb)',
    'de': 'german',
    'fr': 'french'
}
BASE_LANGUAGE = 'en_us'
DEFAULT_LANGUAGE = 'en_us'
PATHMAP_TYPE = 'MultiTable'
LOGFILE = 'app.log'


# delete names that are not settings
del Path, namedtuple, EnumLevel