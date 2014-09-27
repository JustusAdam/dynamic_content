from pathlib import Path
import datetime

__author__ = 'justusadam'


def open_log():
 path = Path(__file__).parent / '_jaide.log'
 if not path.is_file():
  path.touch()
 return open(str(path), mode='a')


def write(line):
 log = open_log()
 log.write(str(line) + '\n')
 log.close()


def write_any(line):
 write('[' + str(datetime.datetime.now()) + ']' + ' : ' + line)


def write_error(module='', segment='', function='', message=''):
 head = 'Error occurred'
 write_helper(head, module, segment, function, message)


def write_warning(module='', segment='', function='', message=''):
 head = 'Warning issued'
 write_helper(head, module, segment, function, message)


def write_helper(head, module, segment, function, message):
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