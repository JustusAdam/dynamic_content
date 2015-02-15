"""
Main file that runs the application.
"""
import argparse
import pathlib
import sys
from framework.util import config, structures
from framework.machinery import component
from framework.includes import log

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
# Python logo Ascii art by @xero -> https://gist.github.com/xero/3555086

__author__ = 'Justus Adam'
__version__ = '0.2.4'


def bool_from_str(string):
    """
    Transform a string 'true' or 'false' into the appropriate boolean value
    :param string:
    :return:
    """
    if not isinstance(string, str):
        return None
    if string.lower() == 'false':
        return False
    elif string.lower() == 'true':
        return True
    else:
        return None


def check_parallel_process():
    """
    If the setproctitle and subprocess dependency can be imported
     this will check if another dynamic_content instance is running
     and prompt whether to kill the other instance or this instance
     or do just continue

    :return: None oor exit process
    """
    try:
        import setproctitle
        import subprocess
    except ImportError:
        return None

    title = 'dynamic_content'

    res = subprocess.check_output(('ps', '-ef'))

    lines = tuple(
        filter(
            lambda a: ' ' + title + ' ' in a,
            res.decode().splitlines()
        )
    )

    if len(lines) != 0:
        log.print_debug(lines)
        user_input = input(
            '\n\nAnother {} process has been detected.\n'
            'Would you like to kill it, in order to start a new one?\n'
            '[y|N]'.format(title)
            )
        if user_input.lower() in ('y', 'yes'):
            subprocess.call(('pkill', 'dynamic_content'))
        else:
            user_input = input(
                'Would you like to exit this process instead? [Y|n]'
            )
            if not user_input.lower() in ('n', 'no'):
                quit(code=0)

    if not setproctitle.getproctitle() == title:
        setproctitle.setproctitle(title)


def update_settings(settings, custom, kwsettings):
    """
    Update the settings dict with the custom settings
    and the settings provided via kwargs.

    Since updating overwrites we update with kwargs first
     and with the custom settings later, since those will usually
     be in a settings file which we anticipate a user is more likely
     to change than the main() call arguments (kwargs) in his/her code

    :param settings: settings dict
    :param custom: extra, custom settings dict
    :param kwsettings: settings provided via kwargs
    :return:
    """
    settings.update(kwsettings)
    settings.update(custom)
    return settings


def prepare_parser():
    """
    Instantiate a argparse cmd line argument parser
     and add the appropriate arguments

    :return: parser
    """

    sbool = ('true', 'false')

    parser = argparse.ArgumentParser()

    # arguments

    parser.add_argument(
        '--mode', '-m',
        choices=('run', 'test', 'debug', 'selftest'),
        default='run'
    )

    parser.add_argument(
        'path', type=str, nargs='?'
    )

    # options

    parser.add_argument('--logfile', type=str)
    parser.add_argument(
        '--loglevel',
        type=str,
        choices=tuple(map(str.lower, structures.LoggingLevel._fields))
        )
    parser.add_argument(
        '--pathmap',
        type=str,
        choices=tuple(map(str.lower, structures.PathMaps._fields))
        )
    parser.add_argument('--port', type=int)
    parser.add_argument('--ssl_port', type=int)
    parser.add_argument(
        '--https_enabled',
        type=str,
        choices=sbool
        )
    parser.add_argument(
        '--http_enabled',
        type=str,
        choices=sbool
        )
    parser.add_argument('--host', type=str)
    parser.add_argument(
        '--server',
        type=str,
        choices=tuple(map(str.lower, structures.ServerTypes._fields))
        )
    parser.add_argument('--ssl_certfile', type=str)
    parser.add_argument('--ssl_keyfile', type=str)

    return parser


def process_cmd_args(settings):
    """
    Get a new parser and parse the command line arguments provided

    :param settings: settings dict
    :return: updated settings dict
    """
    parser = prepare_parser()

    startargs = parser.parse_args()

    assert startargs.mode

    settings['mode'] = startargs.mode

    pd = startargs.path if startargs.path else '.'

    settings['project_dir'] = str(pathlib.Path(pd).resolve())

    https_enabled = bool_from_str(startargs.https_enabled)
    if https_enabled is not None:
        settings['https_enabled'] = https_enabled

    http_enabled = bool_from_str(startargs.http_enabled)
    if http_enabled is not None:
        settings['http_enabled'] = http_enabled

    if startargs.logfile:
        settings['logfile'] = startargs.logfile
    if startargs.loglevel:
        settings['logging_level'] = getattr(
            structures.LoggingLevel, startargs.loglevel.upper()
        )
    if startargs.port or startargs.host or startargs.ssl_port:
        settings['server'] = dict(
            host=(startargs.host
                  if startargs.host
                  else settings['server']['host']),
            port=(startargs.port
                  if startargs.port
                  else settings['server']['port']),
            ssl_port=(startargs.ssl_port
                      if startargs.ssl_port
                      else settings['server']['ssl_port']),
            )
    if startargs.server:
        settings['server_type'] = getattr(
            structures.ServerTypes, startargs.server.upper()
        )
    if startargs.ssl_certfile:
        settings['ssl_certfile'] = startargs.ssl_certfile
    if startargs.ssl_keyfile:
        settings['ssl_keyfile'] = startargs.ssl_keyfile

    return settings


@component.inject('settings')
def get_settings(settings):
    """
    It felt cleaner to provide the settings via dependency injection.

    Otherwise this function is kind of redundant.

    It does however take the implementation details for obtaining the
     settings away from the main function, which is desirable.

    :param settings: injected settings
    :return: settings dict
    """
    return settings


def get_custom_settings(startargs):
    """
    Read the provided settings file.

    :param startargs: parsed command line arguments
    :return:
    """
    dir_ = pathlib.Path(startargs['project_dir'])
    file = 'settings.yml'
    return config.read_config(
        str(dir_ / file)
    )


def main():
    """
    Things to do to start the app.

    :return: None
    """

    settings = get_settings()

    startargs = process_cmd_args({})

    custom_settings = get_custom_settings(startargs)

    update_settings(settings, custom_settings, startargs)

    sys.path = [settings['project_dir']] + sys.path

    # omitted, due to issues
    # check_parallel_process()

    log.print_debug(startargs['mode'])

    if startargs['mode'] == 'run':

        from framework import application

        a = application.Application()
        a.start()

    elif startargs['mode'] == 'test':
        import nose
        import importlib
        nose.main(
            module=importlib.import_module(
                settings.get(
                    'test_dir'
                ).replace('/', '.')
            )
        )


if __name__ == '__main__':
    main()
