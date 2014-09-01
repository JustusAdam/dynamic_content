__author__ = 'justusadam'

from .request_handler import RequestHandler
from .database import Database
from .module_operations import Module

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def register_installed_modules():
    Module().register_installed_modules()