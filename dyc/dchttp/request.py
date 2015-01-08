from urllib import parse


__author__ = 'Justus Adam'
__version__ = '0.1.1'


class Request(object):
    __slots__ = (
        'path',
        'headers',
        'query',
        'method',
        'client'
    )

    def __init__(self, path, method, query, headers):
        self.headers = headers
        self.path = path
        self.method = method.lower()
        self.query = query
        self.client = None

    @classmethod
    def from_path_and_post(cls, path, method, headers, query_string=None):
        parsed = parse.urlsplit(path)
        query = parse.parse_qs(query_string) if query_string else parse.parse_qs(parsed.query)
        path = parsed.path
        return cls(path, method, query, headers)
