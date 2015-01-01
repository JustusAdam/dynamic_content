import functools

from dyc.errors import exceptions
from .. import _component
from dyc.util import decorators, typesafe


__author__ = 'justusadam'


_typecheck = {
    int: str.isnumeric,
    str: lambda a: True
}


class _AbstractSegment(object):
    def __init__(self, name, handler=None):
        self.name = name
        self.handler = handler


class Segment(dict, _AbstractSegment):
    def __init__(self, name, handler=None, **kwargs):
        super().__init__(**kwargs)
        _AbstractSegment.__init__(self, name, handler)
        self.wildcard = None


class WildcardSegment(_AbstractSegment):
    def __init__(self, handler):
        super().__init__('**', handler=handler)


class TypeArg(object):
    @typesafe.typesafe
    def __init__(self, name:str, t):
        self.name = name
        self.type = t


class HandlerContainer(object):
    items = {
        'get', 'post'
    }

    def __init__(self, get=None, post=None):
        self.get = get
        self.post = post

    def __getattr__(self, item:str):
        if isinstance(item, str) and item.lower() in self.items:
            return super().__getattribute__(self, item.lower())
        raise AttributeError('Attribute ' + str(item) + ' could not be found')

    def __setattr__(self, key, value):
        if isinstance(key, str) and key.lower() in self.items:
            super().__setattr__(key.lower(), value)
        else:
            super().__setattr__(key, value)


typemap = {
    'int': int,
    'str': str,
    'integer': int,
    'string': str,
    'float': float
}


def parse_path(path:str):
    def _inner(segment:str):
        if segment.startswith('{') and segment.endswith('}'):
            t, *name = segment[1:-1].split(' ')
            if len(name) == 0:
                return typemap[t]
            elif len(name) == 1:
                return TypeArg(name[0], typemap[t])
            else:
                raise exceptions.ControllerError('Name cannot contain spaces')
        else:
            return segment
    for a in path.split('/'):
        yield _inner(a)


@_component.Component('PathMap')
class PathMapper(Segment):
    def __init__(self, **kwargs):
        super().__init__('/', **kwargs)
        self._controller_classes = []

    def add_path(self, path:str, handler):
        path = path[1:] if path.startswith('/') else path
        path = parse_path(path)

        *path_segments, destination = path

        new = old = self

        for segment in path_segments:
            if segment == '**':
                raise exceptions.ControllerError('Midsection cannot be wildcard')
            elif isinstance(segment, str):
                new = old.setdefault(segment, Segment(segment))
            elif isinstance(segment, type):
                new = old.setdefault(segment, Segment(None))
            elif isinstance(segment, TypeArg):
                new = old.setdefault(segment.type, Segment(segment.name))
            else:
                raise TypeError('Expected Type <str> or <type> not ' + str(type(segment)))

            if not isinstance(new, Segment):
                if isinstance(segment, str):
                    new = old[segment] = Segment(segment, new)
                elif isinstance(segment, type):
                    new = old[segment] = Segment(None, new)
                elif isinstance(segment, TypeArg):
                    new = old[segment.type] = Segment(segment.name, new)
                else:
                    raise TypeError('Expected Type <str> or <type> not ' + str(type(segment)))
            old = new

        m = new

        def add_to_container(container, handler_func):
            for a in handler_func.method:
                if getattr(container, a) is None:
                    setattr(container, a, handler_func)
                else:
                    raise exceptions.ControllerError('Overwriting set Handlers is not allowed')

        if destination == '**':
            if m.wildcard is None:
                m.wildcard = HandlerContainer(**{a.lower():handler for a in handler.method})
            elif isinstance(m.wildcard, HandlerContainer):
                add_to_container(m.wildcard, handler)
            else:
                raise exceptions.ControllerError
        elif destination in m:
            s = m[destination]
            if isinstance(s, Segment):
                if s.handler is None:
                    s.handler = HandlerContainer(**{a.lower():handler for a in handler.method})
                else:
                    add_to_container(s.handler, handler)
            elif isinstance(s, HandlerContainer):
                add_to_container(s, handler)
            else:
                raise exceptions.ControllerError('Overwriting set Handlers is not allowed')
        else:
            m[destination] = HandlerContainer(**{a.lower():handler for a in handler.method})

    @decorators.catch(exception=(exceptions.ControllerError, PermissionError), return_value='error', log_error=True, print_error=True)
    def __call__(self, model, url):
        handler = self.get_handler(str(url.path), url.method, model)
        element = handler.func
        if element.query is True:
            return handler(url.query)
        elif url.query:
            if isinstance(element.query, str):
                return handler(**{element.query: url.query.get(element.query, None)})
            elif isinstance(element.query, (list, tuple, set)):
                return handler(**{a : url.query.get(a, None) for a in element.query})
            elif isinstance(element.query, dict):
                return handler(**{b : url.query.get(a, None) for a, b in element.query.items()})
        else:
            if element.query is False:
                return handler()
            else:
                return

    def get_handler(self, path:str, method, *args, **kwargs):
        origin = path
        path = path.split('/')[1:] if path.startswith('/') else path.split('/')
        iargs, ikwargs = [], {}
        wildcard = getattr(self.wildcard, method) if self.wildcard is not None else None
        segment_chain = [self]

        def get_new(old, segment:str):

            def handle_type(segment, t):
                try:
                    x = old[t]
                    if isinstance(x, Segment) and x.name:
                        ikwargs[x.name] = t(segment)
                    else:
                        iargs.append(t(segment))
                    return x
                except KeyError:
                    raise exceptions.PathNotFound(segment)

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
                if new.wildcard and getattr(new.wildcard, method) is not None:
                    wildcard = functools.partial(getattr(new.wildcard, method), *iargs, **ikwargs)
            else:
                break

            try:
                new = get_new(segment_chain[-1], segment)
            except exceptions.PathNotFound:
                break
            segment_chain.append(new)


        else:
            handler = new.handler if isinstance(new, Segment) else new
            try:
                handler_func = getattr(handler, method)
            except AttributeError:
                raise AttributeError('Unrecognized Request method ' + repr(method))
            if not handler_func is None:
                ikwargs.update(kwargs)
                return functools.partial(handler_func, *args + tuple(iargs), **ikwargs)


        if wildcard is None:
            raise exceptions.MethodHandlerNotFound('Mo handler found for request method ' + method + ' for path ' + origin)
        else:
            wildcard.keywords.update(kwargs)
            return functools.partial(wildcard.func, *wildcard.args + args + (origin, ), **wildcard.keywords)
