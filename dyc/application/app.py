import importlib
import functools
import os
import threading
import traceback
from http import server

from dyc.backend import orm
from dyc import core
from dyc.includes import settings, log


# enable https
if settings.HTTPS_ENABLED:
    import ssl

from dyc.util import console, typesafe, lazy, catch_vardump, structures
from dyc import dchttp
from dyc.errors import exceptions
from . import config as _config


__author__ = 'Justus Adam'
__version__ = '0.2.2'


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
        if settings.RUNLEVEL == settings.RunLevel.DEBUG:
            log.write_info('app starting')
        super().__init__()
        lazy.Loadable.__init__(self)
        self.config = config
        self.decorator = core.get_component('TemplateFormatter')

    @core.inject_method(cmw='Middleware')
    def load(self, cmw):
        if settings.RUNLEVEL == settings.RunLevel.DEBUG:
            log.write_info('loading components')
        console.print_info('Loading Components ... ')
        console.print_info('Loading Middleware ...')
        cmw.load(settings.MIDDLEWARE)
        console.print_info('Loading Modules ...')
        self.load_modules()
        cmw.finalize()

    @lazy.ensure_loaded
    def run(self):
        console.print_name()
        if settings.RUNLEVEL == settings.RunLevel.DEBUG:
            log.write_info('starting server')
        if settings.SERVER_TYPE == settings.ServerTypes.PLAIN:
            self.run_http_server_loop()
        elif settings.SERVER_TYPE == settings.ServerTypes.WSGI:
            self.run_wsgi_server_loop()

    def load_modules(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            import dyc.tss

            dyc.tss.init_tables()
            dyc.tss.initialize()

        else:
            for module in settings.MODULES:
                importlib.import_module(module, 'dyc.modules')

    def http_callback(self, request):
        return self.process_request(request)

    @staticmethod
    def wsgi_make_request(ssl_enabled, environ):
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
        else:
            query = None
        return dchttp.Request.from_path_and_post(
            host=environ['HTTP_HOST'],
            path=environ['PATH_INFO'],
            headers={
                k: environ[k] for k in search_headers if k in environ
                },
            method=method,
            query_string=query,
            ssl_enabled=ssl_enabled
        )

    def wsgi_callback(self, ssl_enabled, environ, start_response):
        request = self.wsgi_make_request(ssl_enabled, environ)
        response = self.process_request(request)

        start_response(
            '{} {}'.format(response.code,
                server.BaseHTTPRequestHandler.responses[response.code][0]),
            [tuple(a) for a in response.headers.items()]
        )
        return [response.body if response.body else ''.encode('utf-8')]

    def run_wsgi_server_loop(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            if settings.HTTPS_ENABLED:
                self.run_wsgi_https_server()
            elif settings.HTTP_ENABLED:
                self.run_wsgi_http_server()
        else:
            if settings.HTTP_ENABLED:
                thttp = threading.Thread(
                    target=self.run_wsgi_http_server,
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if settings.HTTPS_ENABLED:
                thttps = threading.Thread(
                    target=self.run_wsgi_https_server,
                    name='DC-HTTPS-Server'
                    )
                thttps.start()

    def run_wsgi_http_server(self):
        httpd = self.config.wsgi_server(
            (self.config.server_arguments.host,
            self.config.server_arguments.port),
            self.config.wsgi_request_handler
        )
        httpd.set_app(functools.partial(self.wsgi_callback, False))
        console.cprint('\n\n')
        console.print_info(
            'Starting HTTP WSGI Server on    Port: {}     and Host: {}'.format(
                self.config.server_arguments.port,
                self.config.server_arguments.host
                ))
        httpd.serve_forever()

    def run_wsgi_https_server(self):
        httpsd = self.config.wsgi_server(
            (
                self.config.server_arguments.host,
                self.config.server_arguments.ssl_port
                ),
            self.config.wsgi_request_handler
            )
        httpsd.set_app(functools.partial(self.wsgi_callback, True))
        httpsd.socket = ssl.wrap_socket(
            httpsd.socket,
            keyfile=settings.SSL_KEYFILE,
            certfile=settings.SSL_CERTFILE,
            server_side=True
            )
        console.cprint('\n\n')
        console.print_info(
            'Starting HTTPS WSGI Server on    Port: {}     and Host:  {}'.format(
                settings.SERVER.host, settings.SERVER.ssl_port)
            )
        httpsd.serve_forever()

    def run_http_server_loop(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            if settings.HTTPS_ENABLED:
                self.run_https_server()
            elif settings.HTTP_ENABLED:
                self.run_http_server()
        else:
            if settings.HTTP_ENABLED:
                thttp = threading.Thread(
                    target=self.run_http_server,
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if settings.HTTPS_ENABLED:
                thttps = threading.Thread(
                    target=self.run_https_server,
                    name='DC-HTTPS-Server'
                    )
                thttps.start()


    def run_http_server(self):
        request_handler = functools.partial(
                            self.config.http_request_handler,
                            self.http_callback,
                            False
                            )

        server_address = (
            self.config.server_arguments.host,
            self.config.server_arguments.port
            )
        httpd = self.config.server_class(server_address, request_handler)
        console.cprint('\n\n')
        console.print_info('Starting Server on host: {}, port:'.format(
            self.config.server_arguments.host,
            self.config.server_arguments.port))
        httpd.serve_forever()

    def run_https_server(self):
        request_handler = functools.partial(
                            self.config.http_request_handler,
                            self.http_callback,
                            True
                            )

        server_address = (
            self.config.server_arguments.host,
            self.config.server_arguments.ssl_port
            )
        httpd = self.config.server_class(server_address, request_handler)
        httpd.socket = ssl.wrap_socket(
            httpd.socket,
            keyfile=settings.SSL_KEYFILE,
            certfile=settings.SSL_CERTFILE,
            server_side=True
            )
        console.cprint('\n\n')
        console.print_info('Starting Server on host: {}, port:'.format(
            self.config.server_arguments.host,
            self.config.server_arguments.port))
        httpd.serve_forever()

    def set_working_directory(self):
        if settings.RUNLEVEL == settings.RunLevel.TESTING: log.write_info(
            'setting working directory ({})'.format(self.config.basedir))
        os.chdir(self.config.basedir)

    @catch_vardump
    @core.inject_method(cmw='Middleware', pathmap='PathMap')
    def process_request(self, request, cmw, pathmap):
        for obj in cmw:
            res = obj.handle_request(request)
            if res is not None:
                return res


        dc_obj = structures.DynamicContent(
            request=request,
            context={
                'parent_page': request.parent_page()
            },
            config={}
            )


        try:
            handler, args, kwargs = pathmap.resolve(request)

            for obj in cmw:
                res = obj.handle_controller(dc_obj, handler, args, kwargs)
                if res is not None:
                    return res

            view = handler(*(dc_obj, ) + args, **kwargs)

        except (exceptions.PathResolving, exceptions.MethodHandlerNotFound) as e:
            log.write_error('Page not found with exception {}'.format(e))
            view = 'error'
            dc_obj.context['title'] = '404 - Page not found'
            dc_obj.context['content'] = (
                '<h3>Pathmapper encountered an error</h3>'
                '<p>Nested Exception:</p>'
                '<code> {} </code>'
                '<p>Stacktrace:</p>'
                '<code> {} </code>'
                ).format(e, traceback.format_exc()) if (
                    settings.RUNLEVEL in
                    (settings.RunLevel.TESTING, settings.RunLevel.DEBUG)
                ) else (
                '<p>The Page you requested could not be found, or'
                'does not support the request method you tried.<p>'
                )

        # Allow view to directly return a response, mainly to handle errors
        if not isinstance(view, dchttp.response.Response):
            for obj in cmw:
                res = obj.handle_view(view, dc_obj)
                if res is not None:
                    return res

            response = self.decorator(view, dc_obj)
        else:
            response = view

        for obj in cmw:
            res = obj.handle_response(request, response)
            if res is not None:
                return res

        return response


if __name__ == '__main__':
    print(
        'This is not the main application file'
        'try invoking main.py from this same package'
    )
