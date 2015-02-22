"""Implementation of the main Application class"""
import threading
import logging

from framework.backend import orm
from framework.util import structures
from framework.machinery import component
from . import loader
from framework.http import appserver


__author__ = 'Justus Adam'
__version__ = '0.2.3'


dc_ascii_art = """

       __                            _                           __             __
  ____/ /_  ______  ____ _____ ___  (_)____    _________  ____  / /____  ____  / /_
 / __  / / / / __ \/ __ `/ __ `__ \/ / ___/   / ___/ __ \/ __ \/ __/ _ \/ __ \/ __/
/ /_/ / /_/ / / / / /_/ / / / / / / / /__    / /__/ /_/ / / / / /_/  __/ / / / /_
\__,_/\__, /_/ /_/\__,_/_/ /_/ /_/_/\___/____\___/\____/_/ /_/\__/\___/_/ /_/\__/
     /____/                            /_____/

"""


class Application(threading.Thread):
    """
    Main Application (should only be instantiated once) inherits from thread
     to release main thread for signal handling
     ergo Ctrl+C will almost immediately stop the application.

    call with .start() to execute in separate thread (recommended)

    call with .run() to execute in main thread (not recommended)
    """
    @component.inject_method('settings')
    def __init__(self, settings, init_function=None):
        if settings['runlevel'] == structures.RunLevel.DEBUG:
            logging.info('app starting')
        super().__init__()
        self.init_function = init_function
        self.settings = settings
        self.threads = []

    def run(self):
        """
        The executable that is run by the Thread

        :return: None
        """
        logging.critical(
            dc_ascii_art
        )
        if self.settings['runlevel'] == structures.RunLevel.DEBUG:
            logging.info('starting server')
        if self.settings['server_type'] == structures.ServerTypes.PLAIN:
            thread_class = appserver.HTTP
        elif self.settings['server_type'] == structures.ServerTypes.WSGI:
            thread_class = appserver.WGSI
        else:
            raise ValueError

        self.start_servers(thread_class)

        self.wait()

    def start_servers(self, thread_class):
        """
        Start all servers defined in settings

        :param thread_class: AppThread subclass to use
        :return: None
        """

        l = loader.Loader()

        if (hasattr(orm.database_proxy, 'database') and (
                orm.database_proxy.database == ':memory:')):
            logging.warning(
                'Using an in-memory database with this software is supported '
                'however bears some restrictions. '
                'SQlite does not support sharing connections between threads '
                'as such you may only use a single server thread '
                'when using an in-memory database.'
                'It is recommended to only use in-memory databases for testing'
            )
            if self.settings['https_enabled']:
                self.threads.append(thread_class(True, l))
            elif self.settings['http_enabled']:
                self.threads.append(thread_class(False, l))
        else:
            l.load()
            if self.settings['https_enabled']:
                self.threads.append(thread_class(True))
            if self.settings['http_enabled']:
                self.threads.append(thread_class(False))

        for thread in self.threads:
            thread.start()

    def wait(self):
        """
        Wait for input to stop the server

        :return: None
        """
        try:
            while True:
                input('Press an Ctrl-C to stop the server ...')
        except KeyboardInterrupt:
            for thread in self.threads:
                thread.join(1)
            raise


if __name__ == '__main__':
    print(
        'This is not the main application file '
        'simply invoke the directory with the '
        'python interpreter'
    )
