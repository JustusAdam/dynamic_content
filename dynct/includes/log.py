import pathlib
import datetime
import functools

__author__ = 'justusadam'


def open_log():
    path = pathlib.Path(__file__).parent / 'app.log'
    if not path.is_file():
        path.touch()
    return open(str(path), mode='a')


def write(line):
    log = open_log()
    log.write(str(line) + '\n')
    log.close()


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