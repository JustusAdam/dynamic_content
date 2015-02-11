"""Implementation of the main Application class"""
import threading
from framework.backend import orm
from framework.includes import log
from framework.util import console, structures
from framework import component
from . import loader
from framework.http import appserver


__author__ = 'Justus Adam'
__version__ = '0.2.3'


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
            log.write_info('app starting')
        super().__init__()
        self.init_function = init_function
        self.settings = settings
        self.threads = []

    def run(self):
        """
        The executable that is run by the Thread

        :return: None
        """
        console.print_name()
        if self.settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('starting server')
        if self.settings['server_type'] == structures.ServerTypes.PLAIN:
            thread_class = appserver.HTTP
        elif self.settings['server_type'] == structures.ServerTypes.WSGI:
            thread_class = appserver.WGSI
        else:
            raise ValueError

        self.start_servers(thread_class)

        self.wait()

    def start_servers(self, thread_class):

        l = loader.Loader()

        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
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
        while True:
            a = input('Press an key to stop the server')
            if a:
                for thread in self.threads:
                    thread.join(0)
                quit(code=0)


if __name__ == '__main__':
    print(
        'This is not the main application file '
        'simply invoke the directory with the '
        'python interpreter'
    )
