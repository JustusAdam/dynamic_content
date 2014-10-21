from errors.exceptions import InvalidInputError, UninitializedValuesError
from urllib import parse as p
from .request import Request

__author__ = 'justusadam'


class Parser(tuple):
    def __init__(self, *item_list, target_identifier='target'):
        for item in item_list:
            if not isinstance(item, str):
                raise InvalidInputError
        self.target_id = target_identifier
        super().__init__(item_list)

    def feed(self, url, post):
        self.url = url
        self.post = post

    def parse(self):
        if not hasattr(self, 'url') or not hasattr(self, 'post'):
            raise UninitializedValuesError
        (address, network_location, path, query, fragment) = p.urlsplit(self.url)
        path = path.split('/')
        mapping = dict(zip(self, path[1:]))

        if not isinstance(query, dict):
            query = p.parse_qs(query)
        if isinstance(self.post, dict):
            post = self.post
        else:
            post = p.parse_qs(self.post)

        if self.target_id in query:
            target = query[self.target_id]
            if len(target) == 1:
                target = target[1]
        elif self.target_id in mapping:
            target = mapping[self.target_id]
        else:
            target = path[1]

        request = Request(target, *path, **query)
        request.type = 'HTTP'
        request.post = post
        for argument in mapping:
            setattr(request, argument, mapping[argument])
        for argument in query:
            setattr(request, argument, query[argument])
        return request