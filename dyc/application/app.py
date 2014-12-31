import functools
import os
import threading
from dyc.backend import orm
from dyc import core

from dyc.core.mvc import model as _model
from dyc.modules.comp import formatter
from dyc.util import typesafe, lazy
from dyc.includes import settings, log

from . import config as _config

__author__ = 'justusadam'


class Application(threading.Thread, lazy.Loadable):
    """
    Main Application (should only be instantiated once) inherits from thread to release main thread for signal handling
     ergo Ctrl+C will almost immediately stop the application.

    call with .start() to execute in separate thread (recommended)

    call with .run() to execute in main thread (not recommended)
    """

    @typesafe.typesafe
    def __init__(self, config:_config.ApplicationConfig=_config.DefaultConfig()):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info(message='app starting')
        super().__init__()
        lazy.Loadable.__init__(self)
        self.config = config

    def load(self):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info(message='loading components')

        self.load_modules()

    @lazy.ensure_loaded
    def run(self):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info(message='starting server')
        self.run_http_server_loop()

    def load_modules(self):
        if hasattr(orm.database_proxy, 'database') and orm.database_proxy.database == ':memory:':
            import dyc.modules.cms.temporary_setup_script

            dyc.modules.cms.temporary_setup_script.init_tables()
            dyc.modules.cms.temporary_setup_script.initialize()
        core.Modules.load()
        core.get_component('ControllerMapping').sort()

    def run_http_server_loop(self):

        def http_callback(url, client):
            model = _model.Model()
            model.client = client
            model.view = core.get_component('ControllerMapping')(model, url)
            decorator = formatter.TemplateFormatter(model=model, url=url)
            return decorator.compile_response()

        request_handler = functools.partial(self.config.http_request_handler, http_callback)

        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, request_handler)
        httpd.serve_forever()

    def set_working_directory(self):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info(
            'setting working directory (' + str(self.config.basedir) + ')')
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass