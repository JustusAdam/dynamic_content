import functools
import os
import threading
from http import server

from dyc.backend import orm
from dyc import core

from dyc.core.mvc import model as _model
from dyc.util import typesafe, lazy, console
from dyc.includes import settings, log
from dyc import dchttp

from . import config as _config


__author__ = 'Justus Adam'
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

    @core.inject_method(cmw='Middleware')
    def load(self, cmw):
        if settings.RUNLEVEL == settings.RunLevel.debug:
            log.write_info(message='loading components')
        console.cprint('Loading Components ... ')
        console.cprint('Loading Middleware ...')
        cmw.load(settings.MIDDLEWARE)
        console.cprint('Loaging Modules ...')
        self.load_modules()
        cmw.finalize()

    @lazy.ensure_loaded
    def run(self):
        if settings.RUNLEVEL == settings.RunLevel.debug:
            log.write_info(message='starting server')
        if settings.SERVER_TYPE == 'plain':
            self.run_http_server_loop()
        elif settings.SERVER_TYPE == 'wsgi':
            self.run_wsgi_server_loop()

    def load_modules(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            import dyc.modules.cms.temporary_setup_script

            dyc.modules.cms.temporary_setup_script.init_tables()
            dyc.modules.cms.temporary_setup_script.initialize()
        else:
            core.Modules.load()

    def http_callback(self, request):
        return self.process_request(request)

    @staticmethod
    def wsgi_make_request(environ):
        search_headers = {
            'CONTENT_TYPE',
            'HTTP_CACHE_CONTROL',
            'HTTP_ACCEPT_ENCODING',
            'HTTP_COOKIE',
            'REMOTE_ADDR',
            'HTTP_CONNECTION',
            'HTTP_USER_AGENT',
            'HTTP_ACCEPT_LANGUAGE'
            }
        method = environ['REQUEST_METHOD'].lower()
        if method == 'post':
            query = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode() + environ['QUERY_STRING']
        elif method == 'get':
            query = environ['QUERY_STRING']
        return dchttp.Request.from_path_and_post(
            path=environ['PATH_INFO'],
            headers={
                k: environ[k] for k in search_headers if k in environ
            },
            method=method,
            query_string=query
        )

    def wsgi_callback(self, environ, start_response):
        print(environ['QUERY_STRING'])
        request = self.wsgi_make_request(environ)

        response = self.process_request(request)

        print(response.headers)

        start_response(
            '{} {}'.format(response.code,
                server.BaseHTTPRequestHandler.responses[response.code][0]),
            [tuple(a) for a in response.headers.items()]
        )
        return [response.body if response.body else ''.encode('utf-8')]

    def run_wsgi_server_loop(self):
        httpd = self.config.wsgi_server(
            (self.config.server_arguments.host,
            self.config.server_arguments.port),
            self.config.wsgi_request_handler
        )
        httpd.set_app(self.wsgi_callback)
        console.cprint(
            'Starting WSGI Server on    Port: {}     and Host: {}'.format(
                self.config.server_arguments.port,
                self.config.server_arguments.host
        ))
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

    @core.inject_method(cmw='Middleware', pathmap='PathMap')
    def process_request(self, request, cmw, pathmap):
        for obj in cmw:
            res = obj.handle_request(request)
            if res is not None:
                return res

        model = _model.Model()
        model.client = request.client
        handler, args, kwargs = pathmap.resolve(request)

        for obj in cmw:
            res = obj.handle_controller(request, handler, args, kwargs)
            if res is not None:
                return res

        view = model.view = handler(*(model, ) + args, **kwargs)

        # Allow view to directly return a response, mainly to handle errors
        if not isinstance(view, dchttp.response.Response):
            for obj in cmw:
                res = obj.handle_view(request, view, model)
                if res is not None:
                    return res

            response = self.decorator(view, model, request)
        else:
            response = view

        for obj in cmw:
            res = obj.handle_response(request, response)
            if res is not None:
                return res

        return response
