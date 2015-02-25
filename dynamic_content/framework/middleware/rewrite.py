"""Url Rewriting middleware"""
from framework import middleware
from framework.http import response


__author__ = 'Justus Adam'
__version__ = '0.1'


class RemoveTrailingSlash(middleware.Handler):
    """
    Remove trailing slashes on requests that are not handled by the file handler
    """
    def handle_request(self, request):
        """
        Overwriting parent method

        :param request:
        :return: Response or None
        """
        if request.path.endswith('/') and not request.path == '/':
            return response.Redirect(
                location=request.path[:-1],
                code=response.HttpResponseCodes.MovedPermanently
                )
        return None
