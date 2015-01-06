from urllib import parse


__author__ = 'Justus Adam'


class Request(object):
    def __init__(self, path, method, query, headers):
        self.headers = headers
        self.path = path
        self.method = method
        self.query = query
        self.client = None

    @classmethod
    def from_path_and_post(cls, path, method, headers, post=None):
        parsed = parse.urlsplit(path)
        query = parse.parse_qs(post) if post else parse.parse_qs(parsed.query)
        path = parsed.path
        return cls(path, method, query, headers)