import pathlib
import datetime
import functools

from . import settings

__author__ = 'justusadam'


_path = pathlib.Path(settings.LOGFILE) if settings.LOGFILE.startswith('/') else pathlib.Path(__file__).parent / settings.LOGFILE
if _path.is_dir():
    raise IsADirectoryError
elif not _path.exists():
    _path.touch()

def open_log():
    return open(str(_path), mode='a')


def write(line):
    with open_log() as log:
        print(line, file=log)


def write_any(line):
    write('[' + str(datetime.datetime.now()) + ']' + ' : ' + line)


def write_helper(head, module='', segment='', function='', message=''):
    out = []
    if module:
        out.append('in module ' + str(module))
    if segment:
        out.append('in segment ' + str(segment))
    if function:
        out.append('in function ' + str(function))
    if message:
        out.append('message: ' + str(message))
    write_any(str(head) + ' ' + ', '.join(out))


write_error = functools.partial(write_helper, 'ERROR occurred')
write_info = functools.partial(write_helper, 'INFO')
write_warning = functools.partial(write_helper, 'WARNING issued')