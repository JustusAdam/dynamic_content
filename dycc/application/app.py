import importlib
import functools
import threading
import traceback
from http import server

from dycc.backend import orm
import dycc
from dycc.includes import settings, log


# enable https
if settings['https_enabled']:
    import ssl

from dycc.util import console, lazy, catch_vardump, structures
from dycc import http, middleware
from dycc.errors import exceptions


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
    def __init__(self, init_function):
        if settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('app starting')
        super().__init__()
        lazy.Loadable.__init__(self)
        self.init_function = init_function
        self.decorator = dycc.get_component('TemplateFormatter')

    def load(self):
        if settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('loading components')
        console.print_info('Loading Components ... ')
        console.print_info('Loading Middleware ...')
        middleware.load(settings['middleware'])
        console.print_info('Loading Modules ...')
        self.load_modules()
        if callable(self.init_function):
            self.init_function()

    @lazy.ensure_loaded
    def run(self):
        console.print_name()
        if settings['runlevel'] == structures.RunLevel.DEBUG:
            log.write_info('starting server')
        if settings['server_type'] == structures.ServerTypes.PLAIN:
            self.run_http_server_loop()
        elif settings['server_type'] == structures.ServerTypes.WSGI:
            self.run_wsgi_server_loop()

    @staticmethod
    def load_modules():
        for module in settings['modules']:
            importlib.import_module('.' + module, 'dycm')

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
            if settings['https_enabled']:
                self.run_wsgi_https_server()
            elif settings['http_enabled']:
                self.run_wsgi_http_server()
        else:
            if settings['http_enabled']:
                thttp = threading.Thread(
                    target=self.run_wsgi_http_server,
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if settings['https_enabled']:
                thttps = threading.Thread(
                    target=self.run_wsgi_https_server,
                    name='DC-HTTPS-Server'
                    )
                thttps.start()

    def run_wsgi_http_server(self):
        from dycc.http import wsgi
        httpd = wsgi.Server(
            (settings['server']['host'],
            settings['server']['port']),
            wsgi.Handler
        )

        httpd.set_app(functools.partial(self.wsgi_callback, False))
        console.cprint('\n\n')
        console.print_info(
            'Starting HTTP WSGI Server on    Port: {}     and Host: {}'.format(
                settings['server']['host'],
                settings['server']['port']
                ))
        httpd.serve_forever()

    def run_wsgi_https_server(self):
        from dycc.http import wsgi
        httpsd = wsgi.Server(
            (settings['server']['host'],
            settings['server']['port']),
            wsgi.Handler
        )
        httpsd.set_app(functools.partial(self.wsgi_callback, True))
        httpsd.socket = ssl.wrap_socket(
            httpsd.socket,
            keyfile=settings['ssl_keyfile'],
            certfile=settings['ssl_certfile'],
            server_side=True
            )
        console.cprint('\n\n')
        console.print_info(
            'Starting HTTPS WSGI Server on    Port: {}     and Host:  {}'.format(
                settings['server']['host'], settings['server']['ssl_port'])
            )
        httpsd.serve_forever()

    def run_http_server_loop(self):
        if (hasattr(orm.database_proxy, 'database')
            and orm.database_proxy.database == ':memory:'):
            if settings['https_enabled']:
                self.run_https_server()
            elif settings['http_enabled']:
                self.run_http_server()
        else:
            if settings['http_enabled']:
                thttp = threading.Thread(
                    target=self.run_http_server,
                    name='DC-HTTP-Server'
                    )
                thttp.start()
            if settings['http_enabled']:
                thttps = threading.Thread(
                    target=self.run_https_server,
                    name='DC-HTTPS-Server'
                    )
                thttps.start()


    def run_http_server(self):
        from dycc.http import request_handler
        from dycc.http import server
        request_handler = functools.partial(
                            request_handler.RequestHandler,
                            self.http_callback,
                            False
                            )

        server_address = (
            settings['server']['host'],
            settings['server']['port']
            )
        httpd = server.ThreadedHTTPServer(server_address, request_handler)
        console.cprint('\n\n')
        console.print_info('Starting Server on host: {}, port:'.format(
            *server_address))
        httpd.serve_forever()

    def run_https_server(self):
        from dycc.http import server
        from dycc.http import request_handler
        request_handler = functools.partial(
                            request_handler.RequestHandler,
                            self.http_callback,
                            True
                            )

        server_address = (
            settings['server']['host'],
            settings['server']['port']
            )
        httpd = server.ThreadedHTTPServer(server_address, request_handler)
        httpd.socket = ssl.wrap_socket(
            httpd.socket,
            keyfile=settings['ssl_keyfile'],
            certfile=settings['ssl_certfile'],
            server_side=True
            )
        console.cprint('\n\n')
        console.print_info('Starting Server on host: {}, port:'.format(
            *server_address))
        httpd.serve_forever()

    @catch_vardump
    @dycc.inject_method(pathmap='PathMap')
    def process_request(self, request, pathmap):
        for mw in middleware.Handler.get_hooks():
            res = mw.handle_request(request)
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

            for mw in middleware.Handler.get_hooks():
                res = mw.handle_controller(dc_obj, handler, args, kwargs)
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
                    settings['runlevel'] in
                    (structures.RunLevel.TESTING, structures.RunLevel.DEBUG)
                ) else (
                '<p>The Page you requested could not be found, or'
                'does not support the request method you tried.<p>'
                )

        # Allow view to directly return a response, mainly to handle errors
        if not isinstance(view, http.response.Response):
            for mw in middleware.Handler.get_hooks():
                res = mw.handle_view(view, dc_obj)
                if res is not None:
                    return res

            response = self.decorator(view, dc_obj)
        else:
            response = view

        for mw in middleware.Handler.get_hooks():
            res = mw.handle_response(request, response)
            if res is not None:
                return res

        return response


if __name__ == '__main__':
    print(
        'This is not the main application file'
        'try invoking main.py from this same package'
    )
