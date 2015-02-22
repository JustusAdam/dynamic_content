import logging
import functools

from framework.machinery import component
from ._settings import SettingsDict

__author__ = 'Justus Adam'
__version__ = '0.1'


@component.inject(SettingsDict)
def get_settings(settings):
    return settings


def inject_settings(func):
    return component.inject(SettingsDict)(func)


def _init_log():

    logfile = get_settings().get('logfile', 'console')

    base = functools.partial(
        logging.basicConfig,
        format='%(asctime)s [%(levelname)9s]:%(message)s',
        level=getattr(
            logging,
            get_settings().get('logging_level', 'warning').upper()
        ),
        datefmt='%m/%d/%Y %I:%M:%S'
    )

    if logfile == 'console':
        base()
    else:
        base(filename=logfile)