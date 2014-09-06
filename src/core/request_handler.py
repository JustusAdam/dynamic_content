from http.server import BaseHTTPRequestHandler
from io import BytesIO
import shutil
from pathlib import Path

from core.database import DatabaseError, Database, escape
from .basic_page_handlers import FileHandler, BasicPageHandler
from tools.http_tools import Url
from tools.config_tools import read_config


__author__ = 'justusadam'

hello = None
bootstrap = None


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if not self.check_path():
            return 0

        get_handler_response = self.get_handler()
        if get_handler_response != 0:
            self.send_error(get_handler_response, *self.responses[get_handler_response])
            return 0

        post_request = self.rfile.read(int(self.headers['Content-Length'])).decode()

        if self.page_handler.process_post(post_request):
            self.send_response(302, *self.responses[302])
            self.send_header("Location", self.get_post_target())
            self.end_headers()
        else:
            self.send_document()
        return 0

    def do_GET(self):
        print(hello)
        if not self.check_path():
            return 0

        get_handler_response = self.get_handler()
        if get_handler_response != 0:
            self.send_error(get_handler_response, *self.responses[get_handler_response])
            return 0

        self.send_document()
        return 0

    def send_document(self):
        handler_response = self.page_handler.compile()
        if not handler_response:
            # TODO send some generic error if handler rejects request
            return
        if handler_response == 200 or handler_response is True:
            document = self.page_handler.encoded_document
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
        else:
            self.send_error(handler_response, *self.responses[handler_response])
            return

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
            self.page_handler = FileHandler(self._url.path, bootstrap)
            return 0
        try:
            db = Database()
        except DatabaseError:
            # TODO figure out which error to raise if database unreachable, currently 'internal server error'
            return 500

        self._url.path = self.translate_alias(str(self._url.path), db)

        if len(self._url.path) == 0:
            return 404

        self.page_handler = BasicPageHandler(self._url, db, hello)
        db = None
        return 0

    def start_setup(self):
        if not read_config(str(Path(__file__).parent / 'config.json'))['setup']:
            return 404
        from .setup import SetupHandler
        self.page_handler = SetupHandler(self._url, bootstrap)
        return 0

    def translate_alias(self, alias, db):
        query_result = db.select('source_id', 'alias', 'where alias = ' + escape(alias)).fetchone()
        if query_result is None:
            query_result = alias
        else:
            query_result = query_result[0]
        return query_result
