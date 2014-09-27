"""
These Server implementations are supposed to handle requests in a non-blocking way, however they don't appear to do so
I suspect it is because the request handler blocks the output stream somehow.
I'll leave them like this for now and come back later when I'e figured out how to best handle requests non-blocking.
"""

import socketserver
from http import server

__author__ = 'justusadam'


class ThreadedHTTPServer(server.HTTPServer, socketserver.ThreadingMixIn): pass


class ForkedHTTPServer(server.HTTPServer, socketserver.ForkingMixIn): pass