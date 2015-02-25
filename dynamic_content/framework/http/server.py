"""
Python servers operating with separate threads for request handling.
"""

import socketserver
from http import server

__author__ = 'Justus Adam'
__version__ = '0.1'


class ThreadedHTTPServer(server.HTTPServer, socketserver.ThreadingMixIn):
    """Server executing requests in a separate thread"""
    pass


class ForkedHTTPServer(server.HTTPServer, socketserver.ForkingMixIn):
    """Server executing each request in a separate process fork"""
    pass
