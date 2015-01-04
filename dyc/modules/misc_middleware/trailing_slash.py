from dyc.core import middleware
from dyc.dchttp import response

__author__ = 'justusadam'


class RemoveTrailingSlash(middleware.Handler):
    def handle_request(self, request):
        if request.path.endswith('/') and not request.path == '/':
            return response.Redirect(request.path[:-1])