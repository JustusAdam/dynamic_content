from framework.machinery import component
from ._settings import SettingsDict

__author__ = 'Justus Adam'
__version__ = '0.1'


@component.inject(SettingsDict)
def get_settings(settings):
    return settings


def inject_settings(func):
    return component.inject(SettingsDict)(func)