__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    return Modules()