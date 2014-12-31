from dyc import core
from dyc.errors import exceptions

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


class _AbstractSegment(object):
    def __init__(self, name, handler=None):
        self.name = name
        self.handler = handler


class Segment(dict, _AbstractSegment):
    def __init__(self, name, handler=None, **kwargs):
        super().__init__(**kwargs)
        _AbstractSegment.__init__(self, name, handler)
        self.types = {}
        self.wildcard = None


class WildcardSegment(_AbstractSegment):
    def __init__(self, handler):
        super().__init__('**', handler=handler)


def parse_path(path:str):
    return path.split('/')



@core.Component('PathMapper')
class PathMapper(object):
    def __init__(self):
        self.segments = Segment('/')

    def add_path(self, path, handler):
        path = parse_path(path)

        *path_segments, destination = path

        m = self.get_path(path_segments, create_unknown=True, allow_wildcard=False)

        if destination in m:
            s = m[destination]
            if isinstance(s, Segment):
                if s.wildcard is None:
                    s.wildcard = handler
                    return
            raise PathHandlerException('Overwriting set Handlers is not allowed')
        else:
            m[destination] = handler

    def __getitem__(self, item):
        *path, item = parse_path(item)
        path = self.get_path(path, create_unknown=False, allow_wildcard=True)
        return path.handler if isinstance(path, Segment) else path

    def get_path(self, path, create_unknown=False, allow_wildcard=True):
        old = self.segments
        new = None

        empty = object()

        if create_unknown:
            for segment in path:
                new = old.setdefault(segment, Segment(segment))
                if not isinstance(new, Segment):
                    new = old[segment] = Segment(segment, new)
                old = new

        else:
            *path, dest = path
            for segment in path:
                new = old.get(segment, empty)
                if not isinstance(new, Segment):
                    if allow_wildcard:
                        return old.wildcard
                    else:
                        raise PathHandlerException
                old = new
            if dest in path:
                return dest
            else:
                raise PathHandlerException

        return new