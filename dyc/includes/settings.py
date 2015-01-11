"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make dynamic_content functional.

Might need to be expanded.
"""
from pathlib import Path
from dyc.util import structures


__version__ = '0.2'
__author__ = 'Justus Adam'


LoggingLevel = structures.EnumLevel('logging', ('log_warnings', 'log_errors', 'throw_errors', 'throw_all'))
RunLevel = structures.EnumLevel('logging', ('testing', 'debug', 'production'))
PathMaps = {
    'multitable',
    'tree'
    }


# the order in this list dictates the order in which these modules will be activated
DEFAULT_MODULES = (
    'admin',
    'users',
    'commons',
    'file',
    'iris',
    'i18n'
    )
FILE_DIRECTORIES = {
    'theme': (
        'custom/themes',
        'themes'
        ),
    'private': 'custom/files/private',
    'public': 'custom/files/public'
    }
MODULES_DIRECTORIES = ('custom/modules', 'modules')
COREMODULES_DIRECTORIES = ('core',)
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
SERVER = structures.ServerArguments(port=9012, host='localhost')
DATABASE = structures.DatabaseArguments(
            'mysql', 'python_cms', True, 'python_cms', 'python_cms', 'localhost')
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
MIDDLEWARE = (
    'dyc.middleware.alias.Middleware',
    'dyc.modules.file.PathHandler',
    'dyc.middleware.trailing_slash.RemoveTrailingSlash'
    )
ANTI_CSRF = True
DEFAULT_HEADERS = {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-cache'
    }
SERVER_TYPE = 'plain'
PROPAGATE_ERRORS = True


# delete names that are not settings
del Path, structures
