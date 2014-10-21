from errors.exceptions import InvalidInputError, UninitializedValueError
from urllib import parse as p
from .request import Request

__author__ = 'justusadam'


class RequestMapper(dict):
    def __init__(self, ar_table):
        self.ar_table = ar_table
        super().__init__()

    def register(self, name, parser):
        self.__setitem__(name, parser)

    def __setitem__(self, key, value):
        if not isinstance(key, str) or not isinstance(value, Parser):
            raise InvalidInputError
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if not item in self:
            return dict.__getitem__(self, self.ar_table[item])
        else:
            return dict.__getitem__(self, item)

    def __call__(self, url):
        return self._parse_url(url)

    def _parse_url(self, url):
        (address, network_location, path, query, fragment) = p.urlsplit(url)
        path = path.split('/')
        return self[path[1]](path, query, fragment)




class Parser(tuple):
    def __init__(self, *item_list):
        for item in item_list:
            if not isinstance(item, str):
                raise InvalidInputError
        super().__init__(item_list)

    def _parse(self, path, query, post):
        if not hasattr(self, 'url') or not hasattr(self, 'post'):
            raise UninitializedValueError

        mapping = dict(zip(self, path))

        if not isinstance(query, dict):
            query = p.parse_qs(query)
        if isinstance(post, dict):
            post = post
        else:
            post = p.parse_qs(post)

        request = Request(path[1], *path[2:])
        request.type = 'HTTP'
        request.post = post
        request.get_query = query
        for argument in mapping:
            setattr(request, argument, mapping[argument])
        for argument in query:
            setattr(request, argument, query[argument])
        if post:
            for argument in post:
                setattr(request, argument, post[argument])
        return request

    def __call__(self, path, query, post):
        return self._parse(path, query, post)