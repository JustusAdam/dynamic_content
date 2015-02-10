"""Implementation of the main Application class"""
import importlib
import functools
import threading
import traceback
from http import server
from framework.includes import log
from framework.util import console, lazy, catch_vardump, structures
from framework import http, middleware, component
from framework.errors import exceptions


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
    @component.inject_method('settings')
    def __init__(self, settings, init_function=None):
        if settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('app starting')
        super().__init__()
        lazy.Loadable.__init__(self)
        self.init_function = init_function
        self.settings = settings

    def load(self):
        """
        Load necessary stuff for the application
        :return: None
        """
        if self.settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('loading components')
        console.print_info('Loading Components ... ')
        from framework import mvc, route, dchp
        console.print_info('Loading Middleware ...')
        middleware.load(self.settings['middleware'])
        console.print_info('Loading Modules ...')
        self.load_modules()
        self.load_formatter()
        if callable(self.init_function):
            self.init_function()
        self.load_apps()

    @component.inject_method('TemplateFormatter')
    def load_formatter(self, formatter):
        self.decorator = formatter

    @component.inject_method('Settings')
    def load_apps(self, settings):
        """
        Load apps

        :return: None
        """
        for module in settings['import']:
            importlib.import_module(module)

    @lazy.ensure_loaded
    def run(self):
        """
        The executable that is run by the Thread

        :return: None
        """
        console.print_name()
        if self.settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('starting server')
        if self.settings['server_type'] == structures.ServerTypes.PLAIN:
            self.run_http_server_loop()
        elif self.settings['server_type'] == structures.ServerTypes.WSGI:
            self.run_wsgi_server_loop()

    def load_modules(self):
        """
        Load modules specified in settings

        :return: None
        """
        for module in self.settings['modules']:
            importlib.import_module('.' + module, 'dycm')

    def http_callback(self, request):
        """
        Callable to return to when a request comes in

        :param request: the issued request
        :return: processed request
        """
        return self.process_request(request)

    @staticmethod
    def wsgi_make_request(ssl_enabled, environ):
        """
        Construct a Request object form the WSGI environ

        :param ssl_enabled: boolean whether ssl is enabled
        :param environ: WSGI's environ dict
        :return: request.Request object
        """
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
        return http.Request.from_path_and_post(
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
        """
        Callback to return to from a WSGI Request

        :param ssl_enabled: boolean indicating whether
            it is a ssl enabled request
        :param environ: WSGI environ dict
        :param start_response: callback
        :return: response body
        """
        request = self.wsgi_make_request(ssl_enabled, environ)
        response = self.process_request(request)

        start_response(
            '{} {}'.format(response.code,
                server.BaseHTTPRequestHandler.responses[response.code][0]),
            list(response.headers.to_tuple())
        )
        return [response.body if response.body else ''.encode('utf-8')]

    def run_wsgi_server_loop(self):
        """
        Spawn WSGI server Thread(s)

        :return: None
        """
        from framework.backend import orm
        if (
            hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'
        ):
            if self.settings['https_enabled']:
                self.run_wsgi_http_server(True)
            elif self.settings['http_enabled']:
                self.run_wsgi_http_server(False)
        else:
            if self.settings['http_enabled']:
                thttp = threading.Thread(
                    target=self.run_wsgi_http_server,
                    args=(False, ),
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if self.settings['https_enabled']:
                thttps = threading.Thread(
                    target=self.run_wsgi_http_server,
                    args=(True, ),
                    name='DC-HTTPS-Server'
                    )
                thttps.start()

    def run_wsgi_http_server(self, ssl_enabled):
        """
        Construct an instance of the WSGI server

        :param ssl_enabled: whether to wrap the socket with (open)ssl
        :return: server instance (already started)
        """
        from framework.http import wsgi

        port = 'ssl_port' if ssl_enabled else 'port'

        httpd = wsgi.Server(
            (self.settings['server']['host'],
            self.settings['server'][port]),
            wsgi.Handler
        )

        httpd.set_app(functools.partial(self.wsgi_callback, ssl_enabled))
        if ssl_enabled:
            import ssl
            httpd.socket = ssl.wrap_socket(
                httpd.socket,
                keyfile=self.settings['ssl_keyfile'],
                certfile=self.settings['ssl_certfile'],
                server_side=True
                )
        console.cprint('\n\n')
        console.print_info(
            'Starting {} WSGI Server on    Port: {}     and Host: {}'.format(
                'HTTPS' if ssl_enabled else 'HTTP',
                self.settings['server']['host'],
                self.settings['server']['port']
                ))
        httpd.serve_forever()
        return httpd

    def run_http_server_loop(self):
        """
        Spawn the http/https servers as specified in settings

        :return: None
        """
        from framework.backend import orm
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            if self.settings['https_enabled']:
                self.run_http_server(True)
            elif self.settings['http_enabled']:
                self.run_http_server(False)
        else:
            if self.settings['http_enabled']:
                thttp = threading.Thread(
                    target=self.run_http_server,
                    args=(False, ),
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if self.settings['http_enabled']:
                thttps = threading.Thread(
                    target=self.run_http_server,
                    args=(True, ),
                    name='DC-HTTPS-Server'
                    )
                thttps.start()

    def run_http_server(self, ssl_enabled):
        """
        Construct a http server and run it

        :param ssl_enabled: whether to enable https
        :return: server instance
        """
        from framework.http import request_handler
        from framework.http import server
        request_handler = functools.partial(
            request_handler.RequestHandler,
            self.http_callback,
            False
            )

        port = 'ssl_port' if ssl_enabled else 'port'

        server_address = (
            self.settings['server']['host'],
            self.settings['server'][port]
            )
        httpd = server.ThreadedHTTPServer(server_address, request_handler)
        if ssl_enabled:
            import ssl
            httpd.socket = ssl.wrap_socket(
                httpd.socket,
                keyfile=self.settings['ssl_keyfile'],
                certfile=self.settings['ssl_certfile'],
                server_side=True
                )
        console.cprint('\n\n')
        console.print_info('Starting Server on host: {}, port:'.format(
            *server_address))
        httpd.serve_forever()

    @catch_vardump
    @component.inject_method(pathmap='PathMap')
    def process_request(self, request, pathmap):
        """
        Respond to a http.request.Request instance

        :param request: the incoming and preprocessed request.
        :param pathmap: injected pathmap component
        :return: http.response.Response object
        """
        res = middleware.Handler.return_call_hooks_with(
            lambda self, request: self.handle_request(request),
            request
        )
        if res is not None:
            return res

        try:
            handler, args, kwargs = pathmap.resolve(request)

            dc_obj = structures.DynamicContent(
                request=request,
                context={
                    'parent_page': request.parent_page()
                },
                config={},
                handler_options=handler.options
            )

            res = middleware.Handler.return_call_hooks_with(
                lambda self, dc_obj, handler, args, kwargs:
                self.handle_controller(dc_obj, handler, args, kwargs),
                dc_obj, handler, args, kwargs
            )
            if res is not None:
                return res

            if not 'no_context' in handler.options or handler.options['no_context'] is True:
                view = handler(*(dc_obj, ) + args, **kwargs)
            elif 'no_context' in handler.options and handler.options['no_context'] is False:
                view = handler(*args, **kwargs)
            else:
                raise TypeError('Expected type {} for "no_context" option in handler, got {}'.format(bool, type(handler.options['no_context'])))

        except (exceptions.PathResolving, exceptions.MethodHandlerNotFound) as e:
            log.write_error('Page not found with exception {}'.format(e))
            view = 'error'

            dc_obj = structures.DynamicContent(
                request=request,
                context={
                    'parent_page': request.parent_page()
                },
                config={},
                handler_options={}
            )


            dc_obj.context['title'] = '404 - Page not found'
            dc_obj.context['content'] = (
                '<h3>Pathmapper encountered an error</h3>'
                '<p>Nested Exception:</p>'
                '<code> {} </code>'
                '<p>Stacktrace:</p>'
                '<code> {} </code>'
                ).format(e, traceback.format_exc()) if (
                    self.settings['runlevel'] in
                    (structures.RunLevel.TESTING, structures.RunLevel.DEBUG)
                ) else (
                '<p>The Page you requested could not be found, or'
                'does not support the request method you tried.<p>'
                )

        # Allow view to directly return a response, mainly to handle errors
        if not isinstance(view, http.response.Response):
            res = middleware.Handler.return_call_hooks_with(
                lambda self, view, dc_obj: self.handle_view(view, dc_obj),
                view, dc_obj
            )
            if res is not None:
                return res

            response = self.decorator(view, dc_obj)
        else:
            response = view

        res = middleware.Handler.return_call_hooks_with(
            lambda self, request, response: self.handle_response(request, response),
            request, response
        )
        if res is not None:
            return res

        return response


if __name__ == '__main__':
    print(
        'This is not the main application file'
        'try invoking main.py from this same package'
    )
