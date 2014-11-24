from .config import DefaultConfig as _default_config

__author__ = 'justusadam'


def Config(**kwargs):
    return _default_config(**kwargs)