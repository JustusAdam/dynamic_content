import sys


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, url):
        self.page_type = None
        self._url = url
        self.content_type = 'text/html'
        self.response = 200
        self.encoding = sys.getfilesystemencoding()
        self._page = None

    def compile(self):
        return ''

    def process_post(self, post_request):
        return 200


class FieldHandler:
    pass


class ContentHandler:
    def __init__(self, url):
        self._url = url
