import os
import threading
from dynct.backend import orm
from dynct import core
from dynct.core import mvc

from dynct.core.mvc import model as _model
from dynct.modules.comp import formatter
from dynct.util import typesafe, lazy
from dynct.includes import settings, log

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
            import dynct.modules.cms.temporary_setup_script
            dynct.modules.cms.temporary_setup_script.init_tables()
            dynct.modules.cms.temporary_setup_script.initialize()
        core.Modules.load()
        mvc.controller_mapper.sort()

    def handle_http_request(self, *args):
        def http_callback(url, client):
            model = _model.Model()
            model.client = client
            model.view = mvc.controller_mapper(model, url)
            decorator = formatter.TemplateFormatter(model=model, url=url)
            return decorator.compile_response()

        return self.config.http_request_handler(http_callback, *args)

    def run_http_server_loop(self):
        server_address = (self.config.server_arguments['host'], self.config.server_arguments['port'])
        httpd = self.config.server_class(server_address, self.handle_http_request)
        httpd.serve_forever()

    def set_working_directory(self):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info('setting working directory (' + str(self.config.basedir) + ')')
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass