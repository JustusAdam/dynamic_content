"""
Main file that runs the application.
"""
import os
import pathlib
import argparse
import sys

__author__ = 'justusadam'

_basedir = pathlib.Path(__file__).parent.parent.resolve()

# if framework is not in the path yet, add it and import it
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))
# print(_basedir.parent)

del _basedir


def main():
    from dyc.includes import settings

    parser = argparse.ArgumentParser()
    parser.add_argument('--runlevel', '-r', type=str, choices=settings.RunLevel.levels)
    parser.add_argument('--logfile', type=str)
    parser.add_argument('--loglevel', type=str, choices=settings.LoggingLevel.levels)

    startargs = parser.parse_args()

    if startargs.runlevel:
        settings.RUNLEVEL = settings.RunLevel[startargs.runlevel]
    if startargs.logfile:
        settings.LOGFILE = startargs.logfile
    if startargs.loglevel:
        settings.LOGGING_LEVEL = settings.LoggingLevel[startargs.loglevel]

    from dyc import application
    from dyc.util import config as _config

    config = _config.read_config('modules/cms/config')
    application.Application(application.Config(server_arguments=config['server_arguments'])).start()


if __name__ == '__main__':
    main()