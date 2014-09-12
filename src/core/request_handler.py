"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""

from http.server import BaseHTTPRequestHandler
from io import BytesIO
import shutil
from pathlib import Path

from core import database_operations

from core.database import DatabaseError, Database
from includes.bootstrap import Bootstrap
from .page_handlers import FileHandler, BasicPageHandler
from framework.url_tools import Url
from framework.config_tools import read_config


__author__ = 'justusadam'


bootstrap = Bootstrap()


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if not self.check_path():
            return 0

        self._url.post_query = self.rfile.read(int(self.headers['Content-Length'])).decode()

        handler_response = self.get_handler()
        if handler_response != 0:
            self.send_error(handler_response, *self.responses[handler_response])
            return 0

        self.send_document()
        return 0

    def do_GET(self):
        if not self.check_path():
            return 0

        handler_response = self.get_handler()
        if handler_response != 0:
            self.send_error(handler_response, *self.responses[handler_response])
            return 0

        self.send_document()
        return 0

    def send_document(self):
        # Eventually this try/catch will send errors and redirects based on exceptions thrown by the handler
        # try:
        document = self.page_handler.compile()
        # except Exception as exception:
        #     print(exception)
        #     self.send_error(404, *self.responses[404])
        #     return 0

        self.send_response(200)
        self.send_header("Content-type", "{content_type}; charset={encoding}".format(
            content_type=self.page_handler.content_type, encoding=self.page_handler.encoding))
        self.send_header("Content-Length", str(len(document)))
        self.end_headers()
        stream = BytesIO()
        stream.write(document)
        stream.seek(0)
        try:
            shutil.copyfileobj(stream, self.wfile)
        finally:
            stream.close()

    def get_post_target(self):
        if self._url.get_query:
            if 'destination' in self._url.get_query:
                return '/' + self._url.get_query['destination']
        return '/'

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

        self.page_handler = None

        if self._url.page_type == 'setup':
            return self.start_setup()
        elif self._url.page_type in bootstrap.FILE_DIRECTORIES.keys():
            self.page_handler = FileHandler(self._url.path)
            return 0
        try:
            db = Database()
            db.connect()
        except DatabaseError:
            # TODO figure out which error to raise if database unreachable, currently 'internal server error'
            return 500

        self._url.path = self.translate_alias(str(self._url.path))

        if len(self._url.path) == 0:
            return 404

        self.page_handler = BasicPageHandler(self._url)
        return 0

    def start_setup(self):
        if not read_config(str(Path(__file__).parent / 'config.json'))['setup']:
            return 404
        from .setup import SetupHandler
        self.page_handler = SetupHandler(self._url)
        return 0

    def translate_alias(self, alias):
        try:
            query_result = database_operations.Alias().get_by_alias(alias)
            return query_result
        except (DatabaseError, TypeError):
            return alias
