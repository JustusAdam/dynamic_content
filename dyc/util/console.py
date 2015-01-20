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


def _print(*args, end=csi + '0m\n', **kwargs):
    print(*args, end=end, **kwargs)


cprint = _print if settings.RUNLEVEL in (settings.RunLevel.DEBUG, settings.RunLevel.TESTING) else lambda *args, **kwargs: None

print_info = functools.partial(cprint, csi + '30m' + str(now()), '[INFO]   ')

print_warning = functools.partial(cprint, csi + '33;22m' + str(now()), '[WARNING]')

print_error = functools.partial(print, csi + '31;1m' + str(now()), '[ERROR]  ')

print_debug = functools.partial(cprint, csi  + '30;22m' + str(now()), '[DEBUG]  ')


dc_ascii_art = """
       __                            _                           __             __
  ____/ /_  ______  ____ _____ ___  (_)____    _________  ____  / /____  ____  / /_
 / __  / / / / __ \/ __ `/ __ `__ \/ / ___/   / ___/ __ \/ __ \/ __/ _ \/ __ \/ __/
/ /_/ / /_/ / / / / /_/ / / / / / / / /__    / /__/ /_/ / / / / /_/  __/ / / / /_
\__,_/\__, /_/ /_/\__,_/_/ /_/ /_/_/\___/____\___/\____/_/ /_/\__/\___/_/ /_/\__/
     /____/                            /_____/

"""

print_name = lambda : print(csi + '0m' + csi + '32;1m', dc_ascii_art, sep='')