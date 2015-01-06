"""
Python servers operating with separate threads for request handling.
"""

import socketserver
from http import server

__author__ = 'Justus Adam'
__version__ = '0.1'


class ThreadedHTTPServer(server.HTTPServer, socketserver.ThreadingMixIn): pass


class ForkedHTTPServer(server.HTTPServer, socketserver.ForkingMixIn): pass
