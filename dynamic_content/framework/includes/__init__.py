import logging
import functools
import time

from framework.machinery import component
from framework.util import time as ftime
from ._settings import SettingsDict

__author__ = 'Justus Adam'
__version__ = '0.2'


@component.inject(SettingsDict)
def get_settings(settings):
    return settings


def inject_settings(func):
    return component.inject(SettingsDict)(func)


def _init_log():

    # TODO add more special format values here
    logfile = get_settings().get('logfile', 'console') % {
        'timestamp': time.time(),
        'time': ftime.utcnow()
    }

    base = functools.partial(
        logging.basicConfig,
        format='%(asctime)s %(levelname)9s [%(name)12s] : %(message)s',
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