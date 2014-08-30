from http.server import BaseHTTPRequestHandler
import io
import sys
import shutil
from urllib.error import HTTPError
from pymysql import DatabaseError
from includes import database
from includes.basic_page_handlers import FileHandler
from tools.http_tools import split_path, join_path, parse_url
from tools.module_tools import get_page_handlers
from tools.config_tools import read_config


__author__ = 'justusadam'


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if not self.check_path():
            return 0
        try:
            page_handler = self.get_handler()
        except HTTPError:
            self.send_error(404, self.responses[404][0], self.responses[404][1])
            return 0

        post_request = self.rfile.read(int(self.headers['Content-Length'])).decode()

        if page_handler.process_post(post_request):
            self.send_response(302, *self.responses[302])
            self.send_header("Location", self.get_post_target())
            self.end_headers()
        else:
            self.send_document(page_handler=page_handler)

        return 0

    def do_GET(self):
        if not self.check_path():
            return 0
        try:
            page_handler = self.get_handler()
        except HTTPError:
            self.send_error(404, *self.responses[404])
            return 0

        self.send_document(page_handler=page_handler)

        return 0

    def send_document(self, page_handler):
        enc = sys.getfilesystemencoding()
        handler_response = page_handler.compile_page()
        print(handler_response)
        if not handler_response:
            # send some error
            return
        if handler_response == 200 or handler_response is True:
            encoded = page_handler.document.encode(enc)
            self.send_response(200)
            self.send_header("Content-type", "{content_type}; charset={encoding}".format(
                content_type=page_handler.content_type, encoding=enc))
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            stream = io.BytesIO()
            stream.write(encoded)
            stream.seek(0)
            try:
                shutil.copyfileobj(stream, self.wfile)
            finally:
                stream.close()
        else:
            self.send_error(handler_response, *self.responses[handler_response])
            return

    def get_post_target(self):
        (path, location, query) = split_path(self.path)
        if query:
            for option in query.split('?'):
                option = option.split('=')
                if option[0] == 'destination':
                    return '/' + option[1]
        return '/'

    def check_path(self):

        (path, location, query) = split_path(path=self.path)

        if path.endswith('/'):
            self.send_response(301)
            self.send_header("Location", join_path(path[:-1], location, query))
            self.end_headers()
            return False
        return True

    def get_handler(self):
        config = read_config('includes/bootstrap')

        (path, location,  get_query) = parse_url(url=self.path)
        print(self.path)
        if path[0] == 'setup':
            if len(path) == 1:
                page_id = 0
            else:
                page_id = int(path[1])
            from includes.setup import page_handler_factory
            return page_handler_factory(page_id=page_id, get_query=get_query)
        elif path[0] in config['FILE_DIRECTORIES'].keys():
            return FileHandler(path)
        else:
            try:
                db_connection = database.Database()
                page_handlers = get_page_handlers(db_connection)
            except DatabaseError:
                # temporary exception
                raise HTTPError(url=self.path, code=404, msg='', fp=None, hdrs=None)

            path = de_alias(path, db_connection)

            if path[0] not in page_handlers.keys():
                raise HTTPError(url=self.path, code=404, msg='', fp=None, hdrs=None)

            page_id = int(path[1])

            if len(path >= 3):
                url_tail = path[2:]
            else:
                url_tail = ''

            ph_callback_module = __import__(page_handlers['module'])
            return ph_callback_module.page_handler_factory(page_id=page_id, url_tail=url_tail, get_query=get_query)


def de_alias(path, db):
    try:
        source = translate_alias('/' + '/'.join([word for word in path]), db)
        return source
    except DatabaseError:
        return path


def translate_alias(alias, db):
    query_result = db.select('source', 'alias', 'where alias = "' + alias + '"')[0]
    # Do things
    return query_result