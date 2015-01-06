import weakref
from dyc.core import middleware


__author__ = 'Justus Adam'
__version__ = '0.1'


class Middleware(middleware.Handler):
    def handle_response(self, request, response_obj):
        pass
