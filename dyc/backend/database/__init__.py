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

from dyc.util.config import read_config


__author__ = 'justusadam'

db_types = {
    'mysql': 'mysql'
}

# HACK setting config path here (hard), needs to be changed

def database_factory():
    config = read_config(str(str(Path(__file__).parent)) + '/../../modules/cms/config')

    db_imp = importlib.import_module('.' + db_types[config['database_type']], __name__)
    return db_imp.Database(config)


Database = database_factory()

del database_factory, db_types