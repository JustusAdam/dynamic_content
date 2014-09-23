"""
This file implements the basis for important default handler types.

It used to describe more functionality but has been refactored to be simpler and cleaner.

What remains are base classes that may be altered in the future but currently only serve as a launching point.

Eventually basic functions that the core demands these classes to implement may be added as empty functions
"""
import sys
from urllib.error import HTTPError
from framework.url_tools import Url


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, url):
        self.page_type = None
        assert isinstance(url, Url)
        self._url = url
        self.content_type = 'text/html'
        self.encoding = sys.getfilesystemencoding()
        self._page = None

    @property
    def encoded(self):
        return self.compiled.encode(self.encoding)

    @property
    def compiled(self):
        return ''

    def process_post(self, post_request):
        return 200

    def is_post(self):
        return bool(self._url.post_query)


class FieldHandler:

    @property
    def compiled(self):
        return ''


class ContentHandler:
    def __init__(self, url):
        self._url = url

    @property
    def compiled(self):
        return ''

class RedirectMixIn(ContentHandler):

    def redirect(self, destination=None):
        if 'destination' in self._url.get_query:
            destination = self._url.get_query['destination'][0]
        elif not destination:
            destination = str(self._url.path.prt_to_str(0,-1))
        raise HTTPError(str(self._url), 302, 'Redirect', [('Location', destination), ('Connection', 'close')], None)