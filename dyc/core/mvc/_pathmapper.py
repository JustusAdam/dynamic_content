import functools
import collections

from dyc.errors import exceptions
from .. import _component
from dyc.util import decorators, typesafe, console
from dyc.includes import settings


__author__ = 'justusadam'


_typecheck = {
    int: str.isnumeric,
    str: lambda a: True
}

class Segment(dict):
    """A Segment of the path structure"""
    def __init__(self, name, handler=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.handler = handler
        self.wildcard = None

    @staticmethod
    def add_to_container(container, handler_func):
        for a in handler_func.method:
            if getattr(container, a) is None:
                setattr(container, a, handler_func)
            else:
                raise exceptions.ControllerError('Overwriting set Handlers is not allowed')


class TypeArg(object):
    """A Path argument with a name."""
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


class PathMap(Segment):
    def __init__(self, **kwargs):
        super().__init__('/', **kwargs)
        self._controller_classes = []

    def __iadd__(self, other):
        if isinstance(other, (tuple, list)) and len(other) == 2:
            path, handler = other
            self.add_path(path, handler)
            return self
        elif isinstance(other, dict):
            path, handler = other['path'], other['handler']
            self.add_path(path, handler)
            return self
        else:
            raise TypeError('Argument must be tuple or list of path and handler')

    def add_path(self, path:str, handler):
        raise NotImplementedError

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
        raise NotImplementedError



class TreePathMap(PathMap):
    @staticmethod
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

    def add_path(self, path:str, handler):
        console.cprint('Registering on path ' + path + '     Handler: ' + repr(handler))
        path = path[1:] if path.startswith('/') else path
        path = self.parse_path(path)

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

        if destination == '**':
            if m.wildcard is None:
                m.wildcard = HandlerContainer(**{a.lower():handler for a in handler.method})
            elif isinstance(m.wildcard, HandlerContainer):
                self.add_to_container(m.wildcard, handler)
            else:
                raise exceptions.ControllerError
        elif destination in m:
            s = m[destination]
            if isinstance(s, Segment):
                if s.handler is None:
                    s.handler = HandlerContainer(**{a.lower():handler for a in handler.method})
                else:
                    self.add_to_container(s.handler, handler)
            elif isinstance(s, HandlerContainer):
                self.add_to_container(s, handler)
            else:
                raise exceptions.ControllerError('Overwriting set Handlers is not allowed')
        else:
            m[destination] = HandlerContainer(**{a.lower():handler for a in handler.method})

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


class MultiTableSegment(Segment):
    def get_handler_container(self, path):
        first, *rest = path

        if rest:
            if first in self:
                b = self[first]
                if isinstance(b, HandlerContainer):
                    b = self[first] = self.__class__(first, b)
                elif not isinstance(b, self.__class__):
                    raise exceptions.ControllerError('Expected Handler, or Segment, found ' + repr(type(b)))
            else:
                b = self[first] = self.__class__(first)

            return b.get_handler_container(rest)
        else:
            a = self.setdefault(first, HandlerContainer())
            if isinstance(a, self.__class__):
                if a.handler is None:
                    a.handler = HandlerContainer()

                a = a.handler
            return a

    def segment_get_handler(self, path:str):
        rest = collections.deque()
        p = path

        while p:
            if p in self:
                if rest:
                    if not isinstance(self[p], self.__class__):
                        raise exceptions.PathResolving(path)
                    return self[p].get_handler('/'.join(rest))
                else:
                    return self[p].handler if isinstance(self[p], self.__class__) else self[p]
            else:
                p, r = p.rsplit('/', 1)
                rest.appendleft(r)
        else:
            p = int(rest[0]) if rest[0].isnumeric() else rest[0]



class MultiTablePathMap(MultiTableSegment, PathMap):
    @staticmethod
    def parse_path(path):
        def split_segments(path:str):
            def _inner(segment):
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
            first, *rest = path.split('/')
            if first != '':
                yield _inner(first)
            for a in rest:
                yield _inner(a)

        segments = split_segments(path)

        r = []
        p = []

        def flush_p():
            if p:
                r.append('/'.join(p))
                p.clear()

        for s in segments:
            if isinstance(s, str):
                p.append(s)
            elif isinstance(s, type) or isinstance(s, TypeArg):
                flush_p()
                r.append(s)
        else:
            flush_p()

        return r


    def add_path(self, path:str, handler):
        self.add_to_container(self.get_handler_container(self.parse_path(path)), handler)

    def get_handler(self, path:str, method, *args, **kwargs):
        return self.segment_get_handler(path, )


_component.Component('PathMap')(
    {
        'multitable': MultiTablePathMap,
        'tree': TreePathMap
    }[settings.PATHMAP_TYPE.lower()]
)