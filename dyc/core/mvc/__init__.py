from .config import Config, DefaultConfig
from . import _pathmapper, controller, model
from .decorator import Autoconf, controller_function, controller_method, controller_class

del _pathmapper

__author__ = 'Justus Adam'


__all__ = [
    'Autoconf',
    'controller_method',
    'controller_function',
    'controller',
    'Config',
    'DefaultConfig',
    'controller_class'
    ]