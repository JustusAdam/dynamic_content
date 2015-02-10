import pathlib
import datetime
import functools

from . import inject_settings

__author__ = 'Justus Adam'
__version__ = '0.1'


@inject_settings
def get_path(settings):
    _path = (
        pathlib.Path(settings['logfile'][1:])
        if settings['logfile'].startswith('/')
        else pathlib.Path(__file__).parent / settings['logfile']
        )
    if _path.is_dir():
        raise IsADirectoryError
    elif not _path.exists():
        _path.touch()
    return _path


def open_log():
    return open(str(get_path()), mode='a')


def write(*stuff):
    with open_log() as log:
        print(*stuff, file=log)


def write_any(*stuff):
    write(datetime.datetime.now(), *stuff)


write_error   = functools.partial(write_any, '[ERROR]  ')
write_info    = functools.partial(write_any, '[INFO]   ')
write_warning = functools.partial(write_any, '[WARNING]')
