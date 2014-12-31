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


class TypeArg(object):
    def __init__(self, name, t):
        self.name = name
        self.type = t


def parse_path(path:str):
    def _inner(segment:str):
        typemap = {
                    'int': int,
                    'str': str,
                    'integer': int,
                    'string': str,
                    'float': float
                }
        if segment.startswith('{') and segment.endswith('}'):
            t, *name = segment[1:-1].split(' ')
            if len(name) == 0:
                return typemap[t]
            elif len(name) == 1:
                return TypeArg(name[0], typemap[t])
            else:
                raise PathHandlerException
        else:
            return segment
    for a in path.split('/'):
        yield _inner(a)


@core.Component('PathMapper')
class PathMapper(object):
    def __init__(self):
        self.segments = Segment('/')

    def add_path(self, path, handler):
        path = parse_path(path)

        *path_segments, destination = path

        old = self.segments
        new = None

        for segment in path_segments:
            if isinstance(segment, str):
                new = old.setdefault(segment, Segment(segment))
            elif isinstance(segment, type):
                new = old.types.setdefault(segment, Segment(segment))
            else:
                raise TypeError('Expected Type <str> or <type> not ' + str(type(segment)))
            if not isinstance(new, Segment):
                new = old[segment] = Segment(segment, new)
            old = new

        m = new

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
        path = self.get_path(path)
        return path.handler if isinstance(path, Segment) else path

    def __call__(self, path, *args, **kwargs):
        *path, last = path.split('/')

        iargs, ikwargs = [], {}

        handler = None

        segment_chain = [self.segments]

        empty = object()

        def get_wildcard():
            for segment in reversed(segment_chain):
                if not segment.wildcard is None:
                    return segment.wildcard
            else:
                raise PathHandlerException

        def get_new(old, segment:str):

            def handle_type(segment, t):
                x = old.types[t]
                if x.name:
                    ikwargs[x.name] = t(segment)
                else:
                    iargs.append(t(segment))
                return x

            if not isinstance(segment, str):
                raise TypeError('Expected type <str> got ' + str(type(segment)))
            try:
                return old[segment]
            except KeyError:
                t = float if segment.isnumeric() else str
                return handle_type(segment, t)

        for segment in path:
            new = get_new(segment_chain[-1], segment)
            segment_chain.append(new)

            if not isinstance(new, Segment):
                handler = get_wildcard()

        if not handler:
            new = get_new(segment_chain[-1], last)
            segment_chain.append(new)
            if isinstance(new, Segment):
                handler = new.handler if new.handler is not None else get_wildcard()
            elif new is empty:
                handler = get_wildcard()
            else:
                handler = new

        iargs.extend(args)
        ikwargs.update(kwargs)
        return handler(*iargs, **ikwargs)