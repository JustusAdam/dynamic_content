"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""
from http import server
import io
import re
import shutil
import sys
import traceback
from urllib.error import HTTPError
import collections
from dyc.dchttp import Request
from dyc.includes import log, settings
from dyc.util import console

__author__ = 'justusadam'


_catch_errors = False

HEADER_SPLIT_REGEX = re.compile("(\S+?)\s*:\s*(\S+)")



class RequestHandler(server.BaseHTTPRequestHandler):
    def __init__(self, callback_function, request, client_address, server):
        self.callback = callback_function
        super().__init__(request, client_address, server)

    def do_POST(self):
        post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        request = Request.from_path_and_post(self.path, 'post', self.headers, post_query)

        return self.do_any(request)

    def do_GET(self):
        request = Request.from_path_and_post(self.path, 'get', self.headers)
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
                log.write_error(message='permission denied for operation ' + str(self.path))
                self.send_error(401, *self.responses[401])
            except TypeError:
                log.write_error(message='value error for operation ' + str(self.path))
                self.send_error(400, *self.responses[400])
            except FileNotFoundError:
                log.write_error(message='file could not be found for operation' + str(self.path))
                self.send_error(404, *self.responses[404])
            except HTTPError as err:
                raise err
            except Exception as exception:
                print(exception)
                traceback.print_tb(sys.exc_info()[2])
                log.write_error('Unexpected error ' + str(exception))
                self.send_error(500, *self.responses[500])

        if _catch_errors:
            return wrapped
        else:
            return function

    def process_http_error(self, error, response=None):
        console.cprint(error)
        if error.code >= 400:
            if error.reason:
                log.write_warning(message='HTTPError, code: ' + str(error.code) + ', message: ' + error.reason)
                self.send_error(error.code, self.responses[error.code][0], error.reason)
            else:
                log.write_warning(
                    message='HTTPError,  code: ' + str(error.code) + ', message: ' + self.responses[error.code][0])
                self.send_error(error.code, *self.responses[error.code])
            return 0
        else:
            self.send_response(error.code)
            if response:
                if response.headers:
                    self.process_headers(*response.headers)
            if error.headers:
                self.process_headers(*error.headers)
        self.end_headers()
        return 0

    def process_headers(self, *headers:tuple):
        for header in headers:
            if isinstance(header, dict):
                for k, v in header.items():
                    self.send_header(k, v)
            elif isinstance(header, str):
                self.send_header(*HEADER_SPLIT_REGEX.match(header).groups())
            elif hasattr(header, '__iter__') and len(header) == 2:
                self.send_header(*header)
            else:
                print(header)
                raise TypeError

    def send_document(self, response):

        self.send_error(response.code) if response.code >= 400 else self.send_response(response.code)

        if response.code == 200:
            response.headers.setdefault("Content-Length", str(len(response.body)))
            headers = collections.ChainMap(response.headers, settings.DEFAULT_HEADERS)
        else:
            headers = response.headers

        self.process_headers(*headers)
        self.end_headers()
        if response.body:
            stream = io.BytesIO()
            stream.write(response.body)
            stream.seek(0)
            try:
                shutil.copyfileobj(stream, self.wfile)
            finally:
                stream.close()
