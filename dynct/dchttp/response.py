from http.cookies import SimpleCookie

__author__ = 'justusadam'


class Response(object):
    encoding = 'utf-8'
    content_type = 'text/html'

    def __init__(self, body=None, code=200, headers=set(), cookies=SimpleCookie()):
        self.body = body
        self.code = code
        self._headers = headers
        self.cookies = cookies

    @property
    def headers(self):
        if self.cookies:
            return self._headers | {str(self.cookies)}
        else:
            return self._headers