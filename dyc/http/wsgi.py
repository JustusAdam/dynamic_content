from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import socketserver

__author__ = 'Justus Adam'
__version__ = '0.1'


class Server(WSGIServer, socketserver.ThreadingMixIn):
    pass


class Handler(WSGIRequestHandler):
    pass
