from .config import DefaultConfig as _default_config
from .config import ApplicationConfig
from .app import Application

__author__ = 'justusadam'


def Config(**kwargs):
    return _default_config(**kwargs)