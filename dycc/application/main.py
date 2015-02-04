import collections
import dycc
import argparse
import pathlib
import sys
from dycc.util import config, structures, console

__doc__ = """
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
__version__ = '0.2.4'


def bool_from_str(string, default=False):
    if not isinstance(string, str):
        return default
    if string.lower() == 'false':
        return False
    elif string.lower() == 'true':
        return True
    else:
        return default


def prepare():

    # print(python_logo_ascii_art)

    print('\n\n\n')

    _basedir = pathlib.Path(__file__).parent.parent.resolve()

    # if framework is not in the path yet, add it and import it
    if not str(_basedir.parent) in sys.path:
        sys.path.append(str(_basedir.parent))

    # os.chdir(str(_basedir))
    # print(_basedir.parent)

    del _basedir

    check_parallel_process()


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

        title = 'dynamic_content'

        res = subprocess.check_output(('ps', '-ef'))

        lines = tuple(filter(
                    lambda a: ' ' + title + ' ' in a,
                    res.decode().splitlines()
                    ))

        if len(lines) != 0:
            console.print_debug(lines)
            a = input(
                '\n\nAnother {} process has been detected.\n'
                'Would you like to kill it, in order to start a new one?\n'
                '[y|N]'.format(title)
                )
            if a.lower() in ('y', 'yes'):
                subprocess.call(('pkill', 'dynamic_content'))
            else:
                a = input(
                    'Would you like to exit this process instead? [Y|n]'
                )
                if not a.lower() in ('n', 'no'):
                    quit(code=0)

        if not setproctitle.getproctitle() == title:
            setproctitle.setproctitle(title)
    except ImportError:
        pass


def harden_settings(settings:dict):
    tuple_type = collections.namedtuple('Settings', *tuple(settings.keys()))
    return tuple_type, tuple_type(**settings)


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

    # This is why this function cannot be moved to another package/module
    settings['dc_basedir'] = str(pathlib.Path(__file__).parent.parent)

    return settings


def check_import_conflict(settings):
    """
    Verify that the application is not being started with dycc in the python path
     since that will cause import naming conflicts

    :param settings: settings dict
    :return: None or quit application
    """

    if settings['dc_basedir'] in sys.path:
        print(
            'Starting thins software in the package directory or adding '
            'the package directory to the path can cause name conflicts '
            'please start this from a different location or don\'t add it '
            'to the path.'
        )
        quit(code=1)


def prepare_parser():
    """
    Instantiate a argparse cmd line argument parser
     and add the appropriate arguments

    :return: parser
    """

    sbool = ('true', 'false')

    parser = argparse.ArgumentParser()
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
    parser.add_argument('--port', '-p', type=int)
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

    settings['https_enabled'] = bool_from_str(startargs.https_enabled, settings['https_enabled'])
    settings['http_enabled'] = bool_from_str(startargs.http_enabled, settings['http_enabled'])

    if startargs.logfile:
        settings['logfile'] = startargs.logfile
    if startargs.loglevel:
        settings['logging_level'] = getattr(structures.LoggingLevel, startargs.loglevel.upper())
    if startargs.port or startargs.host or startargs.ssl_port:
        settings['server'] = dict(
            host=startargs.host if startargs.host else settings['server']['host'],
            port=startargs.port if startargs.port else settings['server']['port'],
            ssl_port=startargs.ssl_port if startargs.ssl_port else settings['server']['ssl_port'],
            )
    if startargs.server:
        settings['server_type'] = getattr(structures.ServerTypes, startargs.server.upper())
    if startargs.ssl_certfile:
        settings['ssl_certfile'] = startargs.ssl_certfile
    if startargs.ssl_keyfile:
        settings['ssl_keyfile'] = startargs.ssl_keyfile

    return settings


@dycc.inject('settings')
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


def main(custom_settings, init_function=None, **kwargs):
    """

    :param custom_settings: your settings file or dict
    :param init_function: some initializer callable that the app thread should call
    :param kwargs: additional settings
    :return: None
    """

    settings = get_settings()

    if isinstance(custom_settings, str):
        settings['custom_settings_path'] = custom_settings
        custom_settings = config.read_config(custom_settings)

    if not isinstance(custom_settings, dict):
        raise TypeError('Expected {},  got {}'.format(dict, type(custom_settings)))

    settings = update_settings(settings, custom_settings, kwargs)

    check_import_conflict(settings)

    prepare()

    process_cmd_args(settings)

    from dycc import application

    application.Application(
        init_function
        ).start()