__author__ = 'justusadam'


class Response(object):
    encoding = 'utf-8'
    content_type = 'text/html'

    def __init__(self, body=None, code=200, headers=set()):
        self.body = body
        self.code = code
        self.headers = headers