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

from includes import bootstrap
from core.handlers.file import PathHandler
from util.url import Url
from util.config import read_config
from modules.users import client
from includes import log
import core
from modules import form
from errors.exceptions import *


__author__ = 'justusadam'


class RequestWrapper:
  def __init__(self, class_, callback):
    self.wrapped_class = class_
    self.callback = callback

  def __call__(self, *args, **kwargs):
    return self.wrapped_class(self.callback, *args, **kwargs)


class RequestHandler(BaseHTTPRequestHandler):

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
    url = Url(self.path, post_query)
    if not form.validation_hook(url):
      self.send_error(403)
      return 0

    return self.do_any(url)

  def do_GET(self):
    # construct Url object from path for accessibility
    url = Url(self.path, False)
    return self.do_any(url)

  def do_any(self, url):
    # construct client information from headers
    client_information = client.ClientInfoImpl(self.headers)

    try:
      page_handler = self.error_wrapper(self.get_handler)(url, client_information)
    except HTTPError as error:
      return self.process_http_error(error)

    try:
      self.error_wrapper(self.send_document)(page_handler)
    except HTTPError as error:
      return self.process_http_error(error, page_handler)
    return 0

  def error_wrapper(self, function):
    def wrapped(*args, **kwargs):
      try:
        return function(*args, **kwargs)
      except AuthorizationRequiredError:
        log.write_error(message='permission denied for operation ' + str(self.path))
        self.send_error(401, *self.responses[401])
      except InvalidInputError:
        log.write_error(message='value error for operation ' + str(self.path))
        self.send_error(400, *self.responses[400])
      except AccessDisabled:
        log.write_error(message='error when accessing directory' + str(self.path))
        self.send_error(405, 'Indexing is not allowed')
      except MissingFileError:
        log.write_error(message='file could not be found for operation' + str(self.path))
        self.send_error(404, *self.responses[404])
      except HTTPError as err:
        raise err
      except Exception as exception:
        print(exception)
        traceback.print_tb(sys.exc_info()[2])
        log.write_error('Unexpected error ' + str(exception))
        self.send_error(500, *self.responses[500])
    return wrapped

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
      raise HTTPError(str(url), 301, 'Destination invalid', [("Location", str(new_dest))], None)

  def get_handler(self, url, client_info):
    # raise HTTPError(str(url), 500, 'Database unreachable', None, None)

    url.path = core.translate_alias(str(url.path))

    if url.page_type == 'setup':
      self.check_path(url)
      return self.start_setup(url)
    elif url.page_type in bootstrap.FILE_DIRECTORIES:
      return PathHandler(url)

    self.check_path(url)

    if len(url.path) == 0:
      raise HTTPError(str(url), 404, None, None, None)

    return self.callback(url, client_info)

  def start_setup(self, url):
    if not read_config('cms/config.json')['setup']:
      raise HTTPError(str(url), 403, 'Request disabled via server config', None, None)
    from core.setup import SetupHandler

    return SetupHandler(url)