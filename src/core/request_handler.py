"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""

from http.server import BaseHTTPRequestHandler
from io import BytesIO
import shutil
from pathlib import Path
from urllib.error import HTTPError
import sys
import traceback

from core import database_operations
from core.database import DatabaseError, Database
from includes.bootstrap import Bootstrap
from .page_handlers import FileHandler, BasicPageHandler
from framework.url_tools import Url
from framework.config_tools import read_config
from includes import log


__author__ = 'justusadam'


bootstrap = Bootstrap()


class RequestHandler(BaseHTTPRequestHandler):

    _url = None

    def do_POST(self):
        if not self.check_path():
            return 0

        self._url.post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        return self.do_any()

    def do_GET(self):
        if not self.check_path():
            return 0
        return self.do_any()

    def do_any(self):
        try:
            page_handler = self.get_handler()
            self.send_document(page_handler)
        except HTTPError as error:
            print(error)
            if error.code >= 400:
                self.send_error(error.code, *self.responses[error.code])
                return 0
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
        # Eventually this try/catch will send errors and redirects based on exceptions thrown by the handler
        # try:
        document = page_handler.encoded
        # except Exception as exception:
        #     print(exception)
        #     self.send_error(404, *self.responses[404])
        #     return 0

        self.send_response(200)
        self.send_header("Content-type", "{content_type}; charset={encoding}".format(
            content_type=page_handler.content_type, encoding=page_handler.encoding))
        self.send_header("Content-Length", str(len(document)))
        self.end_headers()
        stream = BytesIO()
        stream.write(document)
        stream.seek(0)
        try:
            shutil.copyfileobj(stream, self.wfile)
        finally:
            stream.close()

    def check_path(self):

        self._url = Url(self.path)

        if self._url.path.trailing_slash:
            new_dest = Url(str(self._url))
            new_dest.path.trailing_slash = False
            self.send_response(301)
            self.send_header("Location", str(new_dest))
            self.end_headers()
            return False
        return True

    def get_handler(self):

        if self._url.page_type == 'setup':
            return self.start_setup()
        elif self._url.page_type in bootstrap.FILE_DIRECTORIES.keys():
            return FileHandler(self._url.path)
        try:
            db = Database()
            db.connect()
        except DatabaseError:
            # TODO figure out which error to raise if database unreachable, currently 'internal server error'
            return 500

        self._url.path = self.translate_alias(str(self._url.path))

        if len(self._url.path) == 0:
            return 404

        return BasicPageHandler(self._url)

    def start_setup(self):
        if not read_config(str(Path(__file__).parent / 'config.json'))['setup']:
            return 404
        from .setup import SetupHandler
        return SetupHandler(self._url)

    def translate_alias(self, alias):
        try:
            query_result = database_operations.Alias().get_by_alias(alias)
            return query_result
        except (DatabaseError, TypeError):
            return alias
