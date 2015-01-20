import functools
from dyc.includes import settings
import datetime


__author__ = 'Justus Adam'
__version__ = '0.2'


csi = '\x1b['

# setting terminal output:
# start with csi (\x1b[) + '3' for foreground, '4' for background
# + optionally intensity ranging from 0 - 7 (start with ';')
# end with 'm'




def now():
    time = datetime.datetime.now()
    time = time - datetime.timedelta(microseconds=time.microsecond)
    return time.time()


cprint = print if settings.RUNLEVEL in (settings.RunLevel.DEBUG, settings.RunLevel.TESTING) else lambda *args, **kwargs: None

print_info = functools.partial(cprint, csi + '32;2m', now(), '[INFO]   ')

print_warning = functools.partial(cprint, csi + '33;22m', now(), '[WARNING]')

print_error = functools.partial(print, csi + '31;1m', now(), '[ERROR]  ')

print_debug = functools.partial(cprint, '30;22m', now(), '[DEBUG]  ')