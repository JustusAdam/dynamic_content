"""Dedicated threading.Thread subclasses that run servers"""

import functools
import threading
import traceback
import logging
from http import server

from framework import middleware, http
from framework.errors import exceptions
from framework.util import structures, catch_vardump
from framework.machinery import component

__author__ = 'Justus Adam'
__version__ = '0.1'


class AppThread(threading.Thread):
    """Custom Thread baseclass"""

    @component.inject_method('settings')
    def __init__(self, settings, ssl_enabled, name, loader=None):
        super().__init__(name=name)
        self.ssl_enabled = ssl_enabled
        self.settings = settings
        self.loader = loader

    def run(self):
        """
        Custom run method
        :return: None
        """
        if self.loader:
            self.loader.load()
        self.load_formatter()
        self.run_server()

    def run_server(self):
        """
        To be overwritten in subclass
        :return:
        """
        raise NotImplementedError

    @component.inject_method('TemplateFormatter')
    def load_formatter(self, formatter):
        """
        Delay loading the formatter
        :param formatter:
        :return:
        """
        self.decorator = formatter

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

            if 'no_context' not in handler.options or handler.options['no_context'] is True:
                view = handler(*(dc_obj, ) + args, **kwargs)
            elif 'no_context' in handler.options and handler.options['no_context'] is False:
                view = handler(*args, **kwargs)
            else:
                raise TypeError(
                    'Expected type {} for "no_context" option in handler'
                    ', got {}'.format(bool, type(handler.options['no_context']))
                )

        except (exceptions.PathResolving,
                exceptions.MethodHandlerNotFound) as e:
            logging.getLogger(__name__).error('Page not found with exception {}'.format(e))
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
                ).format(e, traceback.format_exc())

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


class WGSI(AppThread):
    """Thread that runs a WSGI server"""
    def __init__(self, ssl_enabled, loader=None, name='WSGI-Server'):
        super().__init__(ssl_enabled, name, loader)

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

    def run_server(self):
        """
        Overwritten method called from parent class
        :return: Server
        """
        from framework.http import wsgi

        port = 'ssl_port' if self.ssl_enabled else 'port'

        httpd = wsgi.Server(
            (self.settings['server']['host'],
            self.settings['server'][port]),
            wsgi.Handler
        )

        httpd.set_app(functools.partial(self.wsgi_callback, self.ssl_enabled))
        if self.ssl_enabled:
            import ssl
            httpd.socket = ssl.wrap_socket(
                httpd.socket,
                keyfile=self.settings['ssl_keyfile'],
                certfile=self.settings['ssl_certfile'],
                server_side=True
                )
        httpd.serve_forever()
        return httpd


class HTTP(AppThread):
    """Plain HTTP server thread"""
    def __init__(self, ssl_enabled, name='HTTP-Server'):
        super().__init__(ssl_enabled, name)

    def http_callback(self, request):
        """
        Callable to return to when a request comes in

        :param request: the issued request
        :return: processed request
        """
        return self.process_request(request)

    def run_server(self):
        """
        Construct a http server and run it

        :return: server instance
        """
        from framework.http import request_handler
        from framework.http import server
        request_handler = functools.partial(
            request_handler.RequestHandler,
            self.http_callback,
            False
            )

        port = 'ssl_port' if self.ssl_enabled else 'port'

        server_address = (
            self.settings['server']['host'],
            self.settings['server'][port]
            )
        httpd = server.ThreadedHTTPServer(server_address, request_handler)
        if self.ssl_enabled:
            import ssl
            httpd.socket = ssl.wrap_socket(
                httpd.socket,
                keyfile=self.settings['ssl_keyfile'],
                certfile=self.settings['ssl_certfile'],
                server_side=True
                )
        httpd.serve_forever()