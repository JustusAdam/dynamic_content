import functools
from framework.util import time
import pathlib
from framework.component import inject

__author__ = 'Justus Adam'
__version__ = '0.1'


def _cache(func):
    class Cache:
        """Another level of indirection"""
        __slots__ = 'cached',

        def __init__(self, cached):
            self.cached = cached

    _cached = Cache(None)

    def inner():
        """wrapper function"""
        if _cached.cached is None:
            _cached.cached = func()
        return _cached.cached

    return inner


@_cache
@inject('settings')
def get_path(settings):
    """
    Get the full file path to the log
    :param settings: the settings dict
    :return: filepath (str)
    """
    dirpath = (
        pathlib.Path(settings['logfile'])
        if 'logfile' in settings
        else get_default_log_path()
        )

    path = dirpath / ''.join(('session-log-', str(time.utcnow()), '.log'))
    if path.exists():
        raise IOError('logfile name exists')
    else:
        path.touch()

    return str(path)


def get_default_log_path():
    """
    Get a default path to the log based on the used platform
    :return:
    """
    # TODO add platform dependant path
    return pathlib.Path(__file__).parent.resolve()


def open_log():
    """
    Open the logfile
    :return: file
    """
    return open(str(get_path()), mode='a')


def write(*args, **kwargs):
    """Write to the log"""
    with open_log() as log:
        print(*args, file=log, **kwargs)


def write_any(*args, **kwargs):
    """Write with time prepended"""
    write(time.utcnow(), *args, **kwargs)


# Write to the log with some standardized information prepended
print_error = write_error = functools.partial(write_any,     '[ERROR]  ')
print_info = write_info = functools.partial(write_any,       '[INFO]   ')
print_warning = write_warning = functools.partial(write_any, '[WARNING]')
print_debug = write_debug = functools.partial(write_any,     '[DEBUG]  ')
