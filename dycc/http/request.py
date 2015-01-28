from urllib import parse


__author__ = 'Justus Adam'
__version__ = '0.1.1'


class Request(object):
    __slots__ = (
        'path',
        'headers',
        'query',
        'method',
        'client',
        'ssl_enabled',
        'host',
        'port'
    )

    def __init__(self, host, port, path:str, method, query, headers, ssl_enabled):
        self.host = host
        self.port = port
        self.headers = headers
        self.path = path
        self.method = method.lower()
        self.query = query
        self.client = None
        self.ssl_enabled = ssl_enabled

    def parent_page(self):
        parent = self.path.rsplit('/', 1)
        if not parent or parent[0] == '':
            return '/'
        else:
            return parent[0]

    @classmethod
    def from_path_and_post(
        cls,
        host,
        path,
        method,
        headers,
        ssl_enabled,
        query_string=None
        ):
        host = host.rsplit(':', 1)
        port = int(host[1]) if len(host) == 2 else None
        host = host[0]
        parsed = parse.urlsplit(path)
        query = (
            parse.parse_qs(query_string)
            if query_string
            else parse.parse_qs(parsed.query)
            )
        path = parsed.path
        return cls(host, port, path, method, query, headers, ssl_enabled)
