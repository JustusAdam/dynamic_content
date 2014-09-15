"""
This file implements the basis for important default handler types.

It used to describe more functionality but has been refactored to be simpler and cleaner.

What remains are base classes that may be altered in the future but currently only serve as a launching point.

Eventually basic functions that the core demands these classes to implement may be added as empty functions
"""
import sys


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, url):
        self.page_type = None
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