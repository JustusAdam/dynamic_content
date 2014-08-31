from http.server import BaseHTTPRequestHandler
from io import BytesIO
import sys
import shutil

from pymysql import DatabaseError

from coremodules.olymp import database
from coremodules.olymp.basic_page_handlers import FileHandler
from tools.http_tools import split_path, join_path, parse_url
from tools.config_tools import read_config


__author__ = 'justusadam'


class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.page_handler = None

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
        if not self.check_path():
            return 0

        get_handler_response = self.get_handler()
        if get_handler_response != 0:
            self.send_error(get_handler_response, *self.responses[get_handler_response])
            return 0

        self.send_document()

        return 0

    def send_document(self):
        enc = sys.getfilesystemencoding()
        handler_response = self.page_handler.compile_page()
        if not handler_response:
            # TODO send some generic error if handler rejects request
            return
        if handler_response == 200 or handler_response is True:
            encoded = self.page_handler.document.encode(enc)
            self.send_response(200)
            self.send_header("Content-type", "{content_type}; charset={encoding}".format(
                content_type=self.page_handler.content_type, encoding=enc))
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            stream = BytesIO()
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

        if path.endswith('/') and path != '/':
            self.send_response(301)
            self.send_header("Location", join_path(path[:-1], location, query))
            self.end_headers()
            return False
        return True

    def get_handler(self):
        bootstrap = read_config('includes/bootstrap')

        (path, location,  get_query) = parse_url(url=self.path)
        if len(path) > 0:
            if path[0] == 'setup' and bootstrap['SETUP']:
                if len(path) == 1:
                    page_id = 0
                else:
                    page_id = int(path[1])
                from src.coremodules.olymp.setup import page_handler_factory
                self.page_handler = page_handler_factory(page_id=page_id, get_query=get_query)
                return 0
            elif path[0] in bootstrap['FILE_DIRECTORIES'].keys():
                self.page_handler = FileHandler(path)
                return 0
        try:
            db_connection = database.Database()
        except DatabaseError:
            # TODO figure out which error to raise if database unreachable, currently 'internal server error'
            return 500

        path = de_alias(path, db_connection)

        if len(path) == 0:
            return 404

        handler_module = db_connection.select('handler_module', 'page_handlers', 'where path_prefix = ' + database.escape(path[0]).fetchone())
        if handler_module is None:
            return 404

        page_id = int(path[1])

        if len(path >= 3):
            url_tail = path[2:]
        else:
            url_tail = ''

        ph_callback_module = __import__(handler_module)
        self.page_handler = ph_callback_module.page_handler_factory(page_id=page_id, url_tail=url_tail,
                                                                    get_query=get_query)
        return 0


def de_alias(path, db):
    if len(path) == 0:
        alias = '/'
    else:
        alias = '/' + '/'.join([word for word in path])
    try:
        source = translate_alias(alias, db)
        return source
    except DatabaseError:
        return path


def translate_alias(alias, db):
    query_result = db.select('source', 'alias', 'where alias = ' + database.escape(alias)).fetchone
    # TODO check if this works
    return query_result