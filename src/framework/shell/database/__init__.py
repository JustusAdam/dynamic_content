from pathlib import Path
import importlib

from framework.tools.config import read_config


__author__ = 'justusadam'


def get_my_folder():
  return str(Path(__file__).parent)


config = read_config(str(get_my_folder()) + '/../../../config')

db_types = {
  'mysql': 'mysql'
}

db_imp = importlib.import_module('.' + db_types[config['database_type']], __name__)


def database_factory():
  return db_imp.Database(config)

escape = db_imp.escape

Database = database_factory

DatabaseError = db_imp.DatabaseError