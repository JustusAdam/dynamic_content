"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""

from http.server import BaseHTTPRequestHandler
from io import BytesIO
import shutil
from urllib.error import HTTPError
import sys
import traceback

from core import database_operations
from core.database import DatabaseError, Database
from includes import bootstrap
from .page_handlers import FileHandler, BasicPageHandler
from framework.url_tools import Url
from framework.config_tools import read_config
from includes import log
import copy


__author__ = 'justusadam'


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        return self.do_any(post_query)

    def do_GET(self):
        return self.do_any()

    def do_any(self, post_query=None):
        url = Url(self.path)
        url.post_query = post_query
        try:
            self.check_path(url)
            page_handler = self.get_handler(url)
            self.send_document(page_handler)
        except HTTPError as error:
            print(error)
            if error.code >= 400:
                if error.reason:
                    log.write_warning(message='HTTPError, code: ' + str(error.code) + ', message: ' + error.reason)
                    self.send_error(error.code, self.responses[error.code][0], error.reason)
                else:
                    log.write_warning(message='HTTPError,  code: ' + str(error.code) + ', message: ' + self.responses[error.code][0])
                    self.send_error(error.code, *self.responses[error.code])
                return 0
            else:
                self.send_response(error.code)
            if error.headers:
                for header in error.headers:
                    self.send_header(*header)
            self.end_headers()
            return 0
        except Exception as exce:
            print("Unexpected error")
            traceback.print_tb(sys.exc_info()[2])
            print(exce)
            log.write_error('Request Handler', function='do_any', message='Unexpected error ' + str(exce))
            self.send_error(500, *self.responses[500])

        return 0

    def send_document(self, page_handler):
        document = page_handler.encoded
        headers = page_handler.headers

        self.send_response(200)
        self.send_header("Content-type", "{content_type}; charset={encoding}".format(
            content_type=page_handler.content_type, encoding=page_handler.encoding))
        self.send_header("Content-Length", str(len(document)))
        for header in headers:
            self.send_header(*header)
        if not bootstrap.BROWSER_CACHING:
            self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        stream = BytesIO()
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
            raise HTTPError(str(url), 301, 'Indexing is prohibited on this server', ("Location", str(new_dest)), None)

    def get_handler(self, url):

        if url.page_type == 'setup':

            return self.start_setup(url)
        elif url.page_type in bootstrap.FILE_DIRECTORIES.keys():
            return FileHandler(url)
        try:
            db = Database()
            db.connect()
        except DatabaseError:
            raise HTTPError(str(url), 500, 'Database unreachable', None, None)

        url.path = self.translate_alias(str(url.path))

        if len(url.path) == 0:
            raise HTTPError(str(url), 404, None, None, None)

        return BasicPageHandler(url)

    def start_setup(self, url):
        if not read_config('config.json')['setup']:
            raise HTTPError(str(url), 403, 'Request disabled via server config', None, None)
        from .setup import SetupHandler
        return SetupHandler(url)

    def translate_alias(self, alias):
        try:
            query_result = database_operations.Alias().get_by_alias(alias)
            return query_result
        except (DatabaseError, TypeError):
            return alias
