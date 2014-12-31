from .config import Config, DefaultConfig
from .decorator import Autoconf, controller_function, controller_method, controller_class
from . import controller, _pathmapper

del _pathmapper

__author__ = 'justusadam'


__all__ = [
    'Autoconf',
    'controller_method',
    'controller_function',
    'controller',
    'Config',
    'DefaultConfig',
    'controller_class'
]