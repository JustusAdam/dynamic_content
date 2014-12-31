from dynct import core
from dynct.errors import exceptions

__author__ = 'justusadam'


_typecheck = {
    int: str.isnumeric,
    str: lambda a: True
}


class PathHandlerException(exceptions.DCException):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.__class__.__name__ + self.message

    __str__ = __repr__


class Segment(dict):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.types = {}
        self.wildcard = None

    def __getitem__(self, item):
        try:
            super().__getitem__(item)
        except KeyError:
            if self.types:
                for t in self.types:
                    if _typecheck[t](item):
                        return self.types[t]
            if not self.wildcard is None:
                return None
            raise

    def __setitem__(self, key, value):
        if key == '**':
            if self.wildcard is None:
                self.wildcard = value
                return
            else:
                raise TypeError('Overwriting a set wildcard is not allowed')
        elif isinstance(key, str):
            if super().__contains__(key):
                raise TypeError('Overwriting a set key is not allowed')
            else:
                super().__setitem__(key, value)
        elif isinstance(key, type):
            if key in self.types:
                raise TypeError('Overwriting a set type is not allowed')
            else:
                self.types[key] = value
                return
        else:
            raise TypeError('Expected type <string> or <type> for item assignment')

    def __contains__(self, item):
        if item == '**':
            return not self.wildcard is None
        elif isinstance(item, str):
            return super().__contains__(item)
        elif isinstance(item, type):
            return item in self.types

    def setdefault(self, k, d=None):
        if self.__contains__(k):
            return self.__getitem__(k)
        else:
            self.__setitem__(k, d)
            return d



def parse_path(path:str):
    return path.split('/')



@core.Component('PathMapper')
class PathMapper(object):
    def __init__(self):
        self.segments = {}

    def add_path(self, path, handler):
        path = parse_path(path)

        m = self.segments

        destination, *path_segments = reversed(path)

        for segment in path_segments:
            m = m.setdefault(segment, Segment(segment))

        try:
            m[destination] = handler
        except TypeError:
            raise