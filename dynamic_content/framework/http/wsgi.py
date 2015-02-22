import logging

from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import socketserver

__author__ = 'Justus Adam'
__version__ = '0.1'


class Server(WSGIServer, socketserver.ThreadingMixIn):
    pass


class Handler(WSGIRequestHandler):
    def log_message(self, format, *args):
        logging.getLogger(__name__).info("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    def log_error(self, format, *args):
        logging.getLogger(__name__).error("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))