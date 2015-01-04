import functools
import os
import threading
from dyc.backend import orm
from dyc import core
from dyc.core import middleware

from dyc.core.mvc import model as _model
from dyc.util import typesafe, lazy, console
from dyc.includes import settings, log
from dyc import dchttp

from . import config as _config

__author__ = 'justusadam'
__version__ = '0.2'


class Application(threading.Thread, lazy.Loadable):
    """
    Main Application (should only be instantiated once) inherits from thread
     to release main thread for signal handling
     ergo Ctrl+C will almost immediately stop the application.

    call with .start() to execute in separate thread (recommended)

    call with .run() to execute in main thread (not recommended)
    """

    @typesafe.typesafe
    def __init__(self, config:_config.ApplicationConfig=_config.DefaultConfig()):
        if settings.RUNLEVEL == settings.RunLevel.debug:
            log.write_info(message='app starting')
        super().__init__()
        lazy.Loadable.__init__(self)
        self.config = config
        self.decorator = core.get_component('TemplateFormatter')

    def load(self):
        if settings.RUNLEVEL == settings.RunLevel.debug:
            log.write_info(message='loading components')
        middleware.cmw.load(settings.MIDDLEWARE)
        self.load_modules()
        middleware.cmw.finalize()

    @lazy.ensure_loaded
    def run(self):
        if settings.RUNLEVEL == settings.RunLevel.debug:
            log.write_info(message='starting server')
        self.run_http_server_loop()

    def load_modules(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            import dyc.modules.cms.temporary_setup_script

            dyc.modules.cms.temporary_setup_script.init_tables()
            dyc.modules.cms.temporary_setup_script.initialize()
        else:
            core.Modules.load()

    def http_callback(self, request):
        for obj in middleware.cmw:
            res = obj.handle_request(request)
            if res is not None:
                return res

        model = _model.Model()
        model.client = request.client
        handler, args, kwargs = core.get_component('PathMap').resolve(request)

        for obj in middleware.cmw:
            res = obj.handle_controller(request, handler, args, kwargs)
            if res is not None:
                return res

        view = model.view = handler(*(model, ) + args, **kwargs)

        # Allow view to directly return a response, mainly to handle errors
        if not isinstance(view, dchttp.response.Response):
            for obj in middleware.cmw:
                res = obj.handle_view(request, view, model)
                if res is not None:
                    return res

            response = self.decorator(view, model, request)
        else:
            response = view

        for obj in middleware.cmw:
            res = obj.handle_response(request, response)
            if res is not None:
                return res

        return response

    def wsgi_callback(self, environ, start_response):
        print(environ)
        print(start_response)


    def run_wisgy_server_loop(self):
        httpd = self.config.wsgi_server(
            (self.config.server_arguments.host,
            self.config.server_arguments.port),
            self.config.wsgi_request_handler
        )
        httpd.set_app(self.wsgi_callback)
        httpd.serve_forever()

    def run_http_server_loop(self):

        request_handler = functools.partial(
                            self.config.http_request_handler,
                            self.http_callback)

        server_address = (
            self.config.server_arguments.host,
            self.config.server_arguments.port
            )
        httpd = self.config.server_class(server_address, request_handler)
        console.cprint('\n\n Starting Server on host: {}, port:'.format(
            self.config.server_arguments.host,
            self.config.server_arguments.port))
        httpd.serve_forever()

    def set_working_directory(self):
        if settings.RUNLEVEL == settings.RunLevel.testing: log.write_info(
            'setting working directory ({})'.format(self.config.basedir))
        os.chdir(self.config.basedir)

    def process_request(self, request):
        pass
