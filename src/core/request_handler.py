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
import copy

from core.database import DatabaseError, Database
from core.comp.page import BasicHandler
from includes import bootstrap
from .file_handler import FileHandler
from framework.url import Url
from framework.config_tools import read_config
from core.users import client
from includes import log
import core


__author__ = 'justusadam'


class RequestHandler(BaseHTTPRequestHandler):
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
    url = Url(self.path, post_query)

    return self.do_any(url)

  def do_GET(self):
    # construct Url object from path for accessibility
    url = Url(self.path, False)
    return self.do_any(url)

  def do_any(self, url):
    # construct client information from headers
    client_information = client.ClientInfoImpl(self.headers)

    try:
      # ensure the request is being redirected, if it has a trailing slash
      self.check_path(url)
      page_handler = self.get_handler(url, client_information)
    except HTTPError as error:
      return self.process_http_error(error)
    except Exception as exce:
      print("Unexpected error")
      traceback.print_tb(sys.exc_info()[2])
      print(exce)
      log.write_error('Request Handler', function='do_any', message='Unexpected error ' + str(exce))
      self.send_error(500, *self.responses[500])
      return 0

    try:
      self.send_document(page_handler)
    except HTTPError as error:
      print('ping')
      return self.process_http_error(error, page_handler)
    except Exception as exce:
      print("Unexpected error")
      traceback.print_tb(sys.exc_info()[2])
      print(exce)
      log.write_error('Request Handler', function='do_any', message='Unexpected error ' + str(exce))
      self.send_error(500, *self.responses[500])
      return 0

    return 0

  def process_http_error(self, error, page_handler=None):
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
      if page_handler:
        if page_handler.headers:
          self.process_headers(*page_handler.headers)
      if error.headers:
        self.process_headers(*error.headers)
    self.end_headers()
    return 0

  def process_headers(self, *headers):
    for header in headers:
      self.send_header(*header)

  def send_document(self, page_handler):
    document = page_handler.encoded
    headers = page_handler.headers

    self.send_response(200)
    self.send_header("Content-type", "{content_type}; charset={encoding}".format(
      content_type=page_handler.content_type, encoding=page_handler.encoding))
    self.send_header("Content-Length", str(len(document)))
    if headers:
      self.process_headers(*headers)
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
      raise HTTPError(str(url), 301, 'Indexing is prohibited on this server', [("Location", str(new_dest))], None)

  def get_handler(self, url, client_info):

    if url.page_type == 'setup':

      return self.start_setup(url, client_info)
    elif url.page_type in bootstrap.FILE_DIRECTORIES.keys():
      return FileHandler(url, client_info)
    try:
      db = Database()
      db.connect()
    except DatabaseError:
      raise HTTPError(str(url), 500, 'Database unreachable', None, None)

    url.path = core.translate_alias(str(url.path))

    if len(url.path) == 0:
      raise HTTPError(str(url), 404, None, None, None)

    return BasicHandler(url, client_info)

  def start_setup(self, url, client_info):
    if not read_config('config.json')['setup']:
      raise HTTPError(str(url), 403, 'Request disabled via server config', None, None)
    from .setup import SetupHandler

    return SetupHandler(url, client_info)