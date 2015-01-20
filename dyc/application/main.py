"""
Main file that runs the application.
"""
python_logo_ascii_art = """
          .?77777777777777$.
          777..777777777777$+
         .77    7777777777$$$
         .777 .7777777777$$$$
         .7777777777777$$$$$$
         ..........:77$$$$$$$
  .77777777777777777$$$$$$$$$.=======.
 777777777777777777$$$$$$$$$$.========
7777777777777777$$$$$$$$$$$$$.=========
77777777777777$$$$$$$$$$$$$$$.=========
777777777777$$$$$$$$$$$$$$$$ :========+.
77777777777$$$$$$$$$$$$$$+..=========++~
777777777$$..~=====================+++++
77777777$~.~~~~=~=================+++++.
777777$$$.~~~===================+++++++.
77777$$$$.~~==================++++++++:
 7$$$$$$$.==================++++++++++.
 .,$$$$$$.================++++++++++~.
         .=========~.........
         .=============++++++
         .===========+++..+++
         .==========+++.  .++
          ,=======++++++,,++,
          ..=====+++++++++=.
                ..~+=...
"""
## Python logo Ascii art by @xero -> https://gist.github.com/xero/3555086

__author__ = 'Justus Adam'
__version__ = '0.2.3'


def prepare():

    # print(python_logo_ascii_art)

    import os
    import pathlib
    import sys

    print('\n\n\n')

    _basedir = pathlib.Path(__file__).parent.parent.resolve()

    # if framework is not in the path yet, add it and import it
    if not str(_basedir.parent) in sys.path:
        sys.path.append(str(_basedir.parent))

    os.chdir(str(_basedir))
    # print(_basedir.parent)

    del _basedir

    import setproctitle
    import subprocess

    title = 'dynamic_content'

    res = subprocess.check_output(('ps', '-ef'))

    lines = tuple(filter(lambda a: ' ' + title + ' ' in a, res.decode().splitlines()))

    if len(lines) != 0:
        print(lines)
        a = input('\n\nAnother {} process has been detected.\nWould you like to kill it, in order to start a new one?\n[y|N]\n\n\n'.format(title))
        if a.lower() in ('y', 'yes'):
            subprocess.call(('pkill', 'dynamic_content'))
        else:
            sys.exit()

    if not setproctitle.getproctitle() == title:
        setproctitle.setproctitle(title)


def main():
    import argparse
    from dyc.includes import settings
    from dyc.util import structures

    parser = argparse.ArgumentParser()
    parser.add_argument('--runlevel', '-r', type=str, choices=tuple(map(str.lower, settings.RunLevel._fields)))
    parser.add_argument('--logfile', type=str)
    parser.add_argument('--loglevel', type=str, choices=tuple(map(str.lower, settings.LoggingLevel._fields)))
    parser.add_argument('--pathmap', type=str, choices=tuple(map(str.lower, settings.PathMaps._fields)))
    parser.add_argument('--port', type=int)
    parser.add_argument('--host')
    parser.add_argument('--server', type=str, choices=tuple(map(str.lower, settings.ServerTypes._fields)))

    startargs = parser.parse_args()

    if startargs.runlevel:
        settings.RUNLEVEL = getattr(settings.RunLevel, startargs.runlevel.upper())
    if startargs.logfile:
        settings.LOGFILE = startargs.logfile
    if startargs.loglevel:
        settings.LOGGING_LEVEL = getattr(settings.LoggingLevel, startargs.loglevel.upper())
    if startargs.port or startargs.host:
        settings.SERVER = type(settings.SERVER)(
            host=startargs.host if startargs.host else settings.SERVER.host,
            port=startargs.port if startargs.port else settings.SERVER.port
            )
    if startargs.server:
        settings.SERVER_TYPE = getattr(settings.ServerTypes, startargs.server.upper())

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
    prepare()
    main()
