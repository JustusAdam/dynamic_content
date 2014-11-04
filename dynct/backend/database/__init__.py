"""
This file is the backbone of all database interaction.

Once the AR is implemented it is strongly advised to use
the AR instead of directly importing and using this file.

Usage:
  - import this module
  - call Database() to get a connection wrapper for database access
  - use the provided update, select, insert etc. methods
  - try to avoid using cursor() directly
  - escape all values using the escape() function provided here
"""

from pathlib import Path
import importlib

from dynct.util.config import read_config


__author__ = 'justusadam'


def get_my_folder():
    return str(Path(__file__).parent)

# TODO let the config be read when calling Database()
# TODO before that make Database() be only called once and not be a singleton!!!
# HACK setting config path here (hard), needs to be changed
config = read_config(str(get_my_folder()) + '/../../modules/cms/config')

# db_types = {
#     'mysql': 'mysql'
# }

new_db_types = {
    'mysql': 'pymysql'
}

db_mod = importlib.import_module(new_db_types[config['database_type']])

def connection():
    return db_mod.connect(**config['database_connection_arguments'])

# db_imp = importlib.import_module('.' + db_types[config['database_type']], __name__)
#
#
# def database_factory():
#     return db_imp.Database(config)
#
#
# escape = db_imp.escape
#
# Database = database_factory
#
# DatabaseError = db_imp.DatabaseError