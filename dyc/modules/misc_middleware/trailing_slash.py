from dyc.core import middleware
from dyc.dchttp import response

__author__ = 'Justus Adam'


class RemoveTrailingSlash(middleware.Handler):
    def handle_request(self, request):
        if request.path.endswith('/') and not request.path == '/':
            return response.Redirect(
                location=request.path[:-1], 
                code=response.HttpResponseCodes.MovedPermanently
                )
        return None