import pathlib
import datetime
import functools

from . import settings

__author__ = 'Justus Adam'
__version__ = '0.1'


_path = pathlib.Path(settings.LOGFILE[1:]) if settings.LOGFILE.startswith('/') else pathlib.Path(__file__).parent / settings.LOGFILE
if _path.is_dir():
    raise IsADirectoryError
elif not _path.exists():
    _path.touch()

def open_log():
    return open(str(_path), mode='a')


def write(*stuff):
    with open_log() as log:
        print(*stuff, file=log)


def write_any(*stuff):
    write(datetime.datetime.now(), *stuff)


write_error   = functools.partial(write_any, '[ERROR]  ')
write_info    = functools.partial(write_any, '[INFO]   ')
write_warning = functools.partial(write_any, '[WARNING]')
