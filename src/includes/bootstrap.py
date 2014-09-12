"""
The implementation of the singleton Bootstrap object which is to consist of the very fundamental,
non-changing, as in not changing within this version of the software, values required to make _jaide functional.

Might need to be expanded.
"""

from framework.singleton import singleton

__author__ = 'justusadam'


@singleton
class Bootstrap:

    def __init__(self):

        self.DEFAULT_MODULES = [
            'admin_pages',
            'theme_engine',
            'iris',
            'commons_engine',
            'user_management'
        ]
        self.TRACKER_TABLE_CREATION_QUERY = 'create table created_tables (id int unsigned not null auto_increment unique primary key, created_table varchar(500) not null unique, source_module_name varchar(500) not null, source_module_id int unsigned not null);'
        self.FILE_DIRECTORIES = {
            'theme': [
                'custom/themes',
                'themes'
            ],
            'private': 'custom/files/private',
            'public': 'custom/files/public'
        }
        self.MODULES_DIRECTORY = 'custom/modules'
        self.NECESSARY_MODULE_ATTRIBUTES = [
            'name',
            'role'
        ]
        self.COREMODULES_DIRECTORY = 'coremodules'
        self.MODULE_CONFIG_NAME = 'config.json'
