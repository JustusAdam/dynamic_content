"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""

from http import server
import io
import shutil
from urllib.error import HTTPError
import sys
import traceback
import copy
import re

from dyc.includes import settings
from dyc.util import url as _url_mod
from dyc.modules.users import client
from dyc.includes import log
from dyc import core
from dyc.modules import form


__author__ = 'justusadam'

_catch_errors = False

HEADER_SPLIT_REGEX = re.compile("(\S+?)\s*:\s*(\S+)")


class RequestHandler(server.BaseHTTPRequestHandler):
    def __init__(self, callback_function, request, client_address, server):
        self.callback = callback_function
        super().__init__(request, client_address, server)

    def do_POST(self):
        """
        Method that gets called by this handler if it receives a post request.

        Post requests have to be handled by the same methods and handlers. This is to avoid that should a form be sent
        which contains incorrect input the content/field handlers can opt to send the provided inputs back as "value"
        fields to not have the user enter everything again.
        :return:
        """
        post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        # construct Url object from path for accessibility
        url = _url_mod.Url(self.path, post_query)
        url.method = 'post'
        if not form.validation_hook(url):
            self.send_error(403)
            return 0

        return self.do_any(url)

    def do_GET(self):
        # construct Url object from path for accessibility
        url = _url_mod.Url(self.path, False)
        url.method = 'get'
        return self.do_any(url)

    def do_any(self, url):
        # construct client information from headers
        client_information = client.ClientInfoImpl(self.headers)

        try:
            response = self.error_wrapper(self.get_response)(url, client_information)
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
        print(error)
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
            if isinstance(header, str):
                self.send_header(*HEADER_SPLIT_REGEX.match(header).groups())
            elif hasattr(header, '__iter__') and len(header) == 2:
                self.send_header(*header)
            else:
                print(header)
                raise TypeError

    def send_document(self, response):
        document = response.body
        headers = response.headers

        if response.code >= 400:
            self.send_error(response.code)
        else:
            self.send_response(response.code)
        if document:
            self.send_header("Content-type", "{content_type}; charset={encoding}".format(
                content_type=response.content_type, encoding=response.encoding))
            self.send_header("Content-Length", str(len(document)))
        if headers:
            self.process_headers(*headers)
        if not settings.BROWSER_CACHING:
            self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        if document:
            stream = io.BytesIO()
            stream.write(document)
            stream.seek(0)
            try:
                shutil.copyfileobj(stream, self.wfile)
            finally:
                stream.close()

    def check_path(self, url):
        if url.path.trailing_slash:
            new_dest = copy.copy(url)
            new_dest.path.trailing_slash = False
            raise HTTPError(str(url), 301, 'Destination invalid', [("Location", str(new_dest))], None)

    def get_response(self, url, client_info):

        url.path = core.translate_alias(str(url.path))

        # self.check_path(url)

        if len(url.path) == 0:
            raise HTTPError(str(url), 404, None, None, None)

        return self.callback(url, client_info)