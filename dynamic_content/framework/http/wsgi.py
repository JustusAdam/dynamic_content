import logging

from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import socketserver

__author__ = 'Justus Adam'
__version__ = '0.1'


class Server(WSGIServer, socketserver.ThreadingMixIn):
    """
    WSGI server executing requests in separate threads
    """
    pass


class Handler(WSGIRequestHandler):
    """
    Custom WSGI Request Handler subclass
    """
    def log_message(self, format, *args):
        """
        Overwritten parent method to log to the logger instead of stderr

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
        Overwritten parent method to log to the logger instead of stderr

        :param format:
        :param args:
        :return:
        """
        logging.getLogger(__name__).error("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))