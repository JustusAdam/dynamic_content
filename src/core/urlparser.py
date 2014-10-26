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

    Calling this class always returns the parser, called with the full, original path, query and post query
    """
    def __init__(self, storage):
        self.ar_table = storage.table('content_handlers')
        super().__init__()

    def register(self, parser_or_list):
        if isinstance(parser_or_list, Parser):
            for i in parser_or_list.names:
                self.__setitem__(i, parser_or_list)
        elif hasattr(parser_or_list, '__iter__'):
            for p in parser_or_list:
                self.register(p)
        else:
            raise InvalidInputError

    def __setitem__(self, key, value):
        if not isinstance(key, str) or not isinstance(value, Parser):
            raise InvalidInputError
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if not item in self:
            return dict.__getitem__(self, self.storage_resolve(item))
        else:
            return dict.__getitem__(self, item)

    def __call__(self, url, post=None):
        return self._parse_url(url, post)

    def _parse_url(self, url, post):
        (address, network_location, path, query, fragment) = p.urlsplit(url)
        path = path.split('/')
        return self[path[1]](path, query, post)

    def storage_resolve(self, name):
        row = self.ar_table.row(path_prefix=name)
        return row['handler_name']


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
    _names = []

    def __init__(self, names, item_list):
        self.names = names
        for item in item_list:
            if not isinstance(item, str):
                raise InvalidInputError
        self._pathargs = tuple(item_list)

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, value):
        if isinstance(value, str):
            self._names = [value]
        elif hasattr(value, '__iter__'):
            self._names = list(value)
        else:
            raise InvalidInputError

    def _parse(self, path, query, post):
        if path[0] == '':
            path = path[1:]

        mapping = dict(zip(self._pathargs, path))

        if not isinstance(query, dict):
            query = p.parse_qs(query)
        if not isinstance(post, dict):
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