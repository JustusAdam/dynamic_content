from .. import Component
import functools
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


class PathNotFound(PathHandlerException):
    pass


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



@Component('PathMapper')
class PathMapper(object):
    def __init__(self):
        self.segments = Segment('/')

    def add_path(self, path, handler):
        path = parse_path(path)

        *path_segments, destination = path

        new = old = self.segments

        for segment in path_segments:
            if segment == '**':
                raise PathHandlerException('Midsection cannot be wildcard')
            elif isinstance(segment, str):
                new = old.setdefault(segment, Segment(segment))
            elif isinstance(segment, type):
                new = old.types.setdefault(segment, Segment(None))
            elif isinstance(segment, TypeArg):
                new = old.types.setdefault(segment.type, Segment(segment.name))
            else:
                raise TypeError('Expected Type <str> or <type> not ' + str(type(segment)))
            if not isinstance(new, Segment):
                new = old[segment] = Segment(segment, new)
            old = new

        if isinstance(destination, str):
            m = new
        elif isinstance(destination, type):
            m = new.types
        else:
            raise TypeError('Expected Type <str> or <type> not ' + str(type(destination)))

        if destination == '**':
            if m.wildcard is None:
                m.wildcard = handler
            else:
                raise PathHandlerException
        elif destination in m:
            s = m[destination]
            if isinstance(s, Segment) and s.handler is None:
                    s.handler = handler
            else:
                raise PathHandlerException('Overwriting set Handlers is not allowed')
        else:
            m[destination] = handler

    def __getitem__(self, item):
        *path, item = parse_path(item)
        path = self.get_path(path)
        return path.handler if isinstance(path, Segment) else path

    def __call__(self, path, *args, **kwargs):
        origin = path
        path= path.split('/')
        iargs, ikwargs = [], {}
        wildcard = None
        segment_chain = [self.segments]

        def get_new(old, segment:str):

            def handle_type(segment, t):
                try:
                    x = old.types[t]
                    if isinstance(x, Segment) and x.name:
                        ikwargs[x.name] = t(segment)
                    else:
                        iargs.append(t(segment))
                    return x
                except KeyError:
                    raise PathNotFound(segment)

            if not isinstance(segment, str):
                raise TypeError('Expected type <str> got ' + str(type(segment)))
            try:
                return old[segment]
            except KeyError:
                t = int if segment.isnumeric() else str
                return handle_type(segment, t)

        new = segment_chain[-1]
        for segment in path:
            if isinstance(new, Segment):
                if new.wildcard:
                    print(iargs, ikwargs)
                    wildcard = functools.partial(new.wildcard, *iargs, **ikwargs)
            else:
                break

            try:
                new = get_new(segment_chain[-1], segment)
            except PathNotFound:
                break
            segment_chain.append(new)


        else:
            if isinstance(new, Segment):
                handler = new.handler
            else:
                handler = new

            iargs.extend(args)
            ikwargs.update(kwargs)
            return handler(*iargs, **ikwargs)

        if wildcard is None:
            raise PathHandlerException
        else:
            return wildcard(*args + (origin, ), **kwargs)
