__author__ = 'justusadam'

from .request_handler import RequestHandler
from .module_operations import register_installed_modules, load_active_modules

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    load_active_modules()