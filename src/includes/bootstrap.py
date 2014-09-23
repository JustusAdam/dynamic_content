"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make _jaide functional.

Might need to be expanded.
"""

from framework.singleton import singleton

__author__ = 'justusadam'


@singleton
class Bootstrap:

    DEFAULT_MODULES = [
        'admin_pages',
        'theme_engine',
        'iris',
        'commons_engine',
        'user_management',
        'internationalization'
    ]
    TRACKER_TABLE_CREATION_QUERY = 'create table created_tables (id int unsigned not null auto_increment unique primary key, created_table varchar(500) not null unique, source_module_name varchar(500) not null, source_module_id int unsigned not null);'
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
    _clenneer_ = 1
