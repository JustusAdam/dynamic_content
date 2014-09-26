"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make _jaide functional.

Might need to be expanded.
"""

__author__ = 'justusadam'


DEFAULT_MODULES = [
    'theme_engine',
    'iris',
    'commons_engine',
    'user_management',
    'internationalization'
]
FILE_DIRECTORIES = {
    'theme': [
        'custom/themes',
        'themes'
    ],
    'private': 'custom/files/private',
    'public': 'custom/files/public'
}
MODULES_DIRECTORY = 'custom/modules'
NECESSARY_MODULE_ATTRIBUTES = [
    'name',
    'role'
]
COREMODULES_DIRECTORY = 'coremodules'
MODULE_CONFIG_NAME = 'config.json'
ALLOW_HIDDEN_FILES = False
# Setting the above option to true will allow access to files starting with a '.' via the file handler/url
# it is highly recommended to NOT set this flag to true!
BROWSER_CACHING = False
HASHING_ALGORITHM = 'sha256'
HASHING_ROUNDS = 100000
HASH_LENGTH = 64
SALT_LENGTH = 16