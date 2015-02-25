"""
Cache pages for reuse later
"""
from framework import middleware


__author__ = 'Justus Adam'
__version__ = '0.1'


class Middleware(middleware.Handler):
    """
    Middleware checking for a cached copy of the page
    """
    def handle_response(self, request, response_obj):
        """
        Cache the response if allowed
        :param request:
        :param response_obj:
        :return:
        """
        pass

    def handle_request(self, request):
        """
        Return cached response if available

        :param request:
        :return:
        """
        pass