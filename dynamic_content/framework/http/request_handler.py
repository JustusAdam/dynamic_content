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
import logging

from framework.http import Request
from framework.machinery import component


__author__ = 'Justus Adam'
__version__ = '0.2'


_catch_errors = False

HEADER_SPLIT_REGEX = re.compile("(\S+?)\s*:\s*(\S+)")


class RequestHandler(server.BaseHTTPRequestHandler):
    """
    Python stdlib RequestHandler subclass for use with this framework
    """
    def __init__(
            self,
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
        """
        Handle an incoming post request

        :return:
        """
        post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        request = Request.from_path_and_post(
            self.headers['Host'],
            self.path, 'post', self.headers, self.ssl_enabled, post_query)
        request.ssl_enabled = self.ssl_enabled
        return self.do_any(request)

    def do_GET(self):
        """
        Handle an incoming GET request

        :return:
        """
        request = Request.from_path_and_post(
            self.headers['Host'],
            self.path,
            'get',
            self.headers,
            self.ssl_enabled
            )
        return self.do_any(request)

    def do_any(self, request):
        """
        Common operations on an incoming request

        :param request:
        :return:
        """
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
        """
        Wrap function to respond with error codes is exceptions are thrown

        :param function: funciton to wrap
        :return:
        """
        def wrapped(*args, **kwargs):
            """
            Wrapper funciton
            :param args: function call arguments
            :param kwargs: function call keyword arguments
            :return: funciton(*args, **kwargs)
            """
            try:
                return function(*args, **kwargs)
            except PermissionError:
                logging.getLogger(__name__).error(
                    'permission denied for operation {}'.format(self.path)
                    )
                self.send_error(401, *self.responses[401])
            except TypeError:
                logging.getLogger(__name__).error(
                    'value error for operation {}'.format(self.path)
                    )
                self.send_error(400, *self.responses[400])
            except FileNotFoundError:
                logging.getLogger(__name__).error(
                    'file could not be found for operation {}'.format(self.path)
                    )
                self.send_error(404, *self.responses[404])
            except HTTPError as err:
                raise err
            except Exception as exception:
                traceback.print_tb(sys.exc_info()[2], file=logging.getLogger(__name__))
                logging.getLogger(__name__).error('Unexpected error {}'.format(exception))
                self.send_error(500, *self.responses[500])

        if _catch_errors:
            return wrapped
        else:
            return function

    def process_http_error(self, error, response=None):
        """
        Steps to take if an error has occurred

        :param error:
        :param response:
        :return:
        """
        logging.getLogger(__name__).error(error)
        if error.code >= 400:
            if error.reason:
                logging.getLogger(__name__).warning(
                    'HTTPError, code: {}, message: {}'.format(
                        error.code, error.reason
                    )
                )
                self.send_error(
                    error.code, self.responses[error.code][0], error.reason
                    )
            else:
                logging.getLogger(__name__).warning(
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
        """
        Transform headers to be sent back

        :param headers:
        :return:
        """
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

    @component.inject_method('settings')
    def send_document(self, settings, response):
        """
        Sending a document back or an error
        :param settings:
        :param response:
        :return:
        """

        if response.code < 400:
            self.send_response(response.code)
        else:
            self.send_error(response.code)

        if response.code == 200:
            response.headers.setdefault(
                "Content-Length", str(len(response.body))
                )
            headers = collections.ChainMap(
                response.headers, settings['default_headers']
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

    def log_message(self, format, *args):
        """
        Overwriting parent method
        to log messages to the logger instead of stderr

        :param format:
        :param args:
        :return:
        """
        logging.getLogger(__name__).info("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    def log_error(self, format, *args):
        """
        Overwriting parent method
        to log messages to the logger instead of stderr

        :param format:
        :param args:
        :return:
        """
        logging.getLogger(__name__).error("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))