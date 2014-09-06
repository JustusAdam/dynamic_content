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
        print('using encoding ' + self.encoding)
        return self._document.encode(self.encoding)

    @property
    def document(self):
        if self._has_document and self.response == 200:
            return self._document
        else:
            return ''

    def compile(self):
        return self.response


class FieldHandler:
    def __init__(self, db):
        self._field = None
        self.db = db
        self._is_compiled = False

    @property
    def field(self):
        if self._is_compiled:
            return self._field
        elif self.compile():
            return self._field
        else:
            return None

    def compile(self):
        self._is_compiled = True
        return True


class ContentHandler:
    def __init__(self, page, db, modules):
        self._page = page
        self._is_compiled = False
        self.db = db
        self.modules = modules

    @property
    def page(self):
        if self._is_compiled:
            return self._page
        elif self.compile():
            return self._page
        else:
            return None

    def compile(self):
        self._is_compiled = True
        return True