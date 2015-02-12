import functools
from framework.util import time
import os
import pathlib
from framework.component import inject

__author__ = 'Justus Adam'
__version__ = '0.1'


def _cache(func):
    class Cache:
        __slots__ = 'cached',

        def __init__(self, cached):
            self.cached = cached

    _cached = Cache(None)

    def inner():
        if _cached.cached is None:
            _cached.cached = func()
        return _cached.cached

    return inner


@_cache
@inject('settings')
def get_path(settings):
    logfile = settings['logfile']
    log_dir = logfile
    dirpath = pathlib.Path(log_dir)
    if not dirpath.exists():
        dirpath = pathlib.Path(__file__).parent.resolve()
    path = dirpath / ''.join(('session-log-', str(time.utcnow()), '.log'))
    if path.exists():
        raise IOError('logfile name exists')
    else:
        path.touch()

    return str(path)


def open_log():
    return open(str(get_path()), mode='a')


def write(*args, **kwargs):
    with open_log() as log:
        print(*args, file=log, **kwargs)


def write_any(*args, **kwargs):
    write(time.utcnow(), *args, **kwargs)


print_error = write_error = functools.partial(write_any,     '[ERROR]  ')
print_info = write_info = functools.partial(write_any,       '[INFO]   ')
print_warning = write_warning = functools.partial(write_any, '[WARNING]')
print_debug = write_debug = functools.partial(write_any,     '[DEBUG]  ')
