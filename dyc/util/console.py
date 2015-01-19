import functools
from dyc.includes import settings
import datetime


__author__ = 'Justus Adam'
__version__ = '0.2'

def now():
    time = datetime.datetime.now()
    time = time - datetime.timedelta(microseconds=time.microsecond)
    return time.time()


cprint = print if settings.RUNLEVEL in (settings.RunLevel.DEBUG, settings.RunLevel.TESTING) else lambda *args, **kwargs: None

print_info = functools.partial(cprint, now(), '[INFO]')

print_warning = functools.partial(cprint, now(), '[WARNING]')

print_error = functools.partial(print, now(), '[ERROR]')