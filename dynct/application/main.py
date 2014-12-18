"""
Main file that runs the application.
"""
import collections
import os
import pathlib
import sys
import re

__author__ = 'justusadam'


_basedir = pathlib.Path(__file__).parent.parent.resolve()

# if framework is not in the path yet, add it and import it
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))
#print(_basedir.parent)

del _basedir

def main():
    from dynct.includes import settings

    startargs = collections.defaultdict(list)
    arg_regex = re.compile('(\w+)=(\w+)')
    for arg in sys.argv[1:]:
        m = re.fullmatch(arg_regex, arg)
        if m: startargs[m.group(1).lower()].append(m.group(2).split(','))

    if 'runlevel' in startargs:
        if len(startargs['runlevel']) != 1:
            raise ValueError
        settings.RUNLEVEL = settings.RunLevel[startargs['runlevel'][0]]

    from dynct import application
    from dynct.util import config as _config

    config = _config.read_config('modules/cms/config')
    application.Application(application.Config(server_arguments=config['server_arguments'])).start()


if __name__ == '__main__':
    main()