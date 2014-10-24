from errors.exceptions import InvalidInputError, UninitializedValueError
from urllib import parse as p
from .request import Request

__author__ = 'justusadam'


class RequestMapper(dict):
    """
    This class maps path prefixes onto url parsers.

    Use it by accessing the items of this class and calling them.

    If a path prefix is not found in this dictionary this class will ask an external AR connection for a mapping of that
    prefix to a parser. If none is found an error is raised.

    Calling this class always returns he parser, called with the full, original path, query and post query
    """
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

    def __call__(self, url, post=None):
        return self._parse_url(url, post)

    def _parse_url(self, url, post):
        (address, network_location, path, query, fragment) = p.urlsplit(url)
        path = path.split('/')
        return self[path[1]](path, query, post)


class Parser:
    """
    Url parser class.

    Per default this class, when called takes a tuple of path query and post query of a url and constructs a request
    object from it according to the value mapping that is given via __init__

    All arguments in all queries and the attributes of the request are attributes of the request object.

    If they clash, an error is thrown

    If you want the arguments of the query or url to receive custom treatment, create a subclass of this class and
    add a method called _process_{your attribute name} it will be called INSTEAD of setattr()
    """
    def __init__(self, *item_list):
        for item in item_list:
            if not isinstance(item, str):
                raise InvalidInputError
        self._pathargs = tuple(item_list)

    def _parse(self, path, query, post):
        if path[0] == '':
            path = path[1:]

        mapping = dict(zip(self._pathargs, path))

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
        for a in [mapping, query, post]:
            request = self.process_arguments(request, **a)
        return request

    def __call__(self, path, query, post):
        return self._parse(path, query, post)

    def process_arguments(self, request, **arguments):
        for i in arguments:
            if hasattr(self, '_process_' + i):
                getattr(self, '_process_' + i)(request, i, arguments[i])
            setattr(request, i, arguments[i])
        return request