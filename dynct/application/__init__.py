from .config import DefaultConfig as _default_config
from dynct.util.misc_decorators import cache

__author__ = 'justusadam'


@cache
def Config(**kwargs):
    return _default_config(**kwargs)