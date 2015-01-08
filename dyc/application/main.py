"""
Main file that runs the application.
"""
s = """

"""

import this
import os
import pathlib
import argparse
import sys


__author__ = 'Justus Adam'
__version__ = '0.2.1'


print('\n\n\n')


_basedir = pathlib.Path(__file__).parent.parent.resolve()


# if framework is not in the path yet, add it and import it
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))
# print(_basedir.parent)

del _basedir


def main():
    from dyc.includes import settings
    from dyc.util import structures

    parser = argparse.ArgumentParser()
    parser.add_argument('--runlevel', '-r', type=str, choices=settings.RunLevel._fields)
    parser.add_argument('--logfile', type=str)
    parser.add_argument('--loglevel', type=str, choices=settings.LoggingLevel._fields)
    parser.add_argument('--pathmap', type=str, choices=settings.PathMaps)
    parser.add_argument('--port', type=int)
    parser.add_argument('--host')
    parser.add_argument('--server', type=str, choices=('wsgi', 'plain'))

    startargs = parser.parse_args()

    if startargs.runlevel:
        settings.RUNLEVEL = getattr(settings.RunLevel,startargs.runlevel)
    if startargs.logfile:
        settings.LOGFILE = startargs.logfile
    if startargs.loglevel:
        settings.LOGGING_LEVEL = getattr(settings.LoggingLevel,startargs.loglevel)
    if startargs.port or startargs.host:
        settings.SERVER = type(settings.SERVER)(
            host=startargs.host if startargs.host else settings.SERVER.host,
            port=startargs.port if startargs.port else settings.SERVER.port
            )
    if startargs.server:
        settings.SERVER_TYPE = startargs.server

    from dyc import application

    application.Application(
        application.Config(
            server_arguments=structures.ServerArguments(
                host=settings.SERVER.host,
                port=settings.SERVER.port
                )
            )
        ).start()


if __name__ == '__main__':
    main()
