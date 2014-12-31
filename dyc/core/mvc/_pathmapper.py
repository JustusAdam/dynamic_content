import functools
from dyc.errors import exceptions
from .. import _component

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


@_component.Component('PathMap')
class PathMapper(Segment):
    def __init__(self, **kwargs):
        super().__init__('/', **kwargs)

    def add_path(self, path:str, handler):
        path = path[1:] if path.startswith('/') else path
        path = parse_path(path)

        *path_segments, destination = path

        new = old = self

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

    def __call__(self, model, path:str, query):
        handler = self.get_handler(path, model)
        element = handler.func
        if element.query is True:
            return handler(query)
        elif query:
            if isinstance(element.query, str):
                return handler(**{element.query: query.get(element.query, None)})
            elif isinstance(element.query, (list, tuple, set)):
                return handler(**{a : query.get(a, None) for a in element.query})
            elif isinstance(element.query, dict):
                return handler(**{b : query.get(a, None) for a, b in element.query.items()})
        else:
            if element.query is False:
                return handler()
            else:
                return



    def get_handler(self, path:str, *args, **kwargs):
        origin = path
        path = path.split('/')[1:] if path.startswith('/') else path.split('/')
        iargs, ikwargs = [], {}
        wildcard = None
        segment_chain = [self]

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
            ikwargs.update(kwargs)
            return functools.partial(handler, *args + tuple(iargs), **ikwargs)

        if wildcard is None:
            raise PathHandlerException
        else:
            return functools.partial(wildcard, *args + (origin, ), **kwargs)
