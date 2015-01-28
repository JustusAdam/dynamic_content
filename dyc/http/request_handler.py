"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received.
This file should not be changed by non-core developers as it
*should* not need altering.
"""
from http import server
import io
import re
import shutil
import sys
import traceback
from urllib.error import HTTPError
import collections
from dyc.http import Request
from dyc.includes import log, settings
from dyc.util import console


__author__ = 'Justus Adam'
__version__ = '0.2'


_catch_errors = False

HEADER_SPLIT_REGEX = re.compile("(\S+?)\s*:\s*(\S+)")


class RequestHandler(server.BaseHTTPRequestHandler):
    def __init__(self,
        callback_function,
        ssl_enabled,
        request,
        client_address,
        server
        ):
        self.callback = callback_function
        self.ssl_enabled = ssl_enabled
        super().__init__(request, client_address, server)

    def do_POST(self):
        post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        request = Request.from_path_and_post(
            self.headers['Host'],
            self.path, 'post', self.headers, self.ssl_enabled, post_query)
        request.ssl_enabled = self.ssl_enabled
        return self.do_any(request)

    def do_GET(self):
        request = Request.from_path_and_post(
            self.headers['Host'],
            self.path,
            'get',
            self.headers,
            self.ssl_enabled
            )
        return self.do_any(request)

    def do_any(self, request):
        try:
            response = self.error_wrapper(self.callback)(request)
        except HTTPError as error:
            return self.process_http_error(error)

        try:
            self.error_wrapper(self.send_document)(response)
        except HTTPError as error:
            return self.process_http_error(error, response)
        return 0

    def error_wrapper(self, function):
        def wrapped(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except PermissionError:
                log.write_error(
                    'permission denied for operation {}'.format(self.path)
                    )
                self.send_error(401, *self.responses[401])
            except TypeError:
                log.write_error(
                    'value error for operation {}'.format(self.path)
                    )
                self.send_error(400, *self.responses[400])
            except FileNotFoundError:
                log.write_error(
                    'file could not be found for operation {}'.format(self.path)
                    )
                self.send_error(404, *self.responses[404])
            except HTTPError as err:
                raise err
            except Exception as exception:
                print(exception)
                traceback.print_tb(sys.exc_info()[2])
                log.write_error('Unexpected error {}'.format(exception))
                self.send_error(500, *self.responses[500])

        if _catch_errors:
            return wrapped
        else:
            return function

    def process_http_error(self, error, response=None):
        console.print_error(error)
        if error.code >= 400:
            if error.reason:
                log.write_warning(
                'HTTPError, code: {}, message: {}'.format(
                    error.code, error.reason
                    )
                )
                self.send_error(
                    error.code, self.responses[error.code][0], error.reason
                    )
            else:
                log.write_warning(
                    'HTTPError,  code: {}, message: {}'.format(
                        error.code, self.responses[error.code][0]
                        )
                    )
                self.send_error(error.code, *self.responses[error.code])
            return 0
        else:
            self.send_response(error.code)
            if response:
                if response.headers:
                    self.process_headers(response.headers)
            if error.headers:
                self.process_headers(error.headers)
        self.end_headers()
        return 0

    def process_headers(self, headers:dict):
        if isinstance(headers, (dict, collections.ChainMap)):
            for k, v in headers.items():
                self.send_header(k, v)
        elif isinstance(headers, (tuple, list, set, frozenset)):
            if isinstance(headers[0], (tuple, list)):
                for header in headers:
                    for k,v in header:
                        self.send_header(k, v)
            else:
                self.send_header(headers[0], headers[1])
        else:
            raise TypeError(
                'Expected headers of type {} or {}, got {}'.format(
                    dict, tuple, type(headers)
                    )
                )

    def send_document(self, response):

        (self.send_error(response.code)
        if response.code >= 400
        else self.send_response(response.code))

        if response.code == 200:
            response.headers.setdefault(
                "Content-Length", str(len(response.body))
                )
            headers = collections.ChainMap(
                response.headers, settings.DEFAULT_HEADERS
                )
        else:
            headers = response.headers

        self.process_headers(headers)
        self.end_headers()
        if response.body:
            stream = io.BytesIO()
            stream.write(response.body)
            stream.seek(0)
            try:
                shutil.copyfileobj(stream, self.wfile)
            finally:
                stream.close()
