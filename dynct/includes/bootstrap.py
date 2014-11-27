"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make _jaide functional.

Might need to be expanded.
"""
from collections import namedtuple

__author__ = 'justusadam'


LoggingLevel = namedtuple('LoggingLevel', ['log_warnings', 'log_errors', 'throw_errors', 'throw_all'])


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