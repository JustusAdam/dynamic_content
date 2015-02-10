from framework import component
from . import _settings

__author__ = 'Justus Adam'
__version__ = '0.1'


@component.inject('settings')
def get_settings(settings):
    return settings


def inject_settings(func):
    return component.inject('settings')(func)