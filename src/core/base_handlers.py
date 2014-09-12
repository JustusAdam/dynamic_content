import sys


__author__ = 'justusadam'


class PageHandler:
    def __init__(self, url):
        self.page_type = None
        self._url = url
        self._document = ''
        self.content_type = 'text/html'
        self.response = 200
        self._has_document = False
        self.encoding = sys.getfilesystemencoding()
        self._page = None

    @property
    def encoded_document(self):
        return self._document.encode(self.encoding)

    @property
    def document(self):
        if self._has_document and self.response == 200:
            return self._document
        else:
            return ''

    def compile(self):
        self._has_document = True
        return self.response

    def process_post(self, post_request):
        return 200


class FieldHandler:
    pass


class ContentHandler:
    def __init__(self, url):
        self._url = url
