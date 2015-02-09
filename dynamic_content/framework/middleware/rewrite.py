from dynamic_content import middleware
from dynamic_content.http import response


__author__ = 'Justus Adam'
__version__ = '0.1'


class RemoveTrailingSlash(middleware.Handler):
    def handle_request(self, request):
        if request.path.endswith('/') and not request.path == '/':
            return response.Redirect(
                location=request.path[:-1],
                code=response.HttpResponseCodes.MovedPermanently
                )
        return None
