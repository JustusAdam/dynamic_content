import functools
import collections
from dyc import dchttp

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
    """Value object for holding handlers to various request types with some convenience methods for value access"""
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
    """Abstract Baseclass for path mappers"""
    def __init__(self, **kwargs):
        super().__init__('/', **kwargs)
        console.cprint('Utilizing PathMapType:   ' + self.__class__.__name__)
        self._controller_classes = []

    def __iadd__(self, other):
        """convenience  function for adding new path handlers"""
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
        """registers given handler at given path"""
        raise NotImplementedError

    @decorators.catch(exception=(exceptions.ControllerError, PermissionError), return_value='error', log_error=True, print_error=True)
    def resolve(self, request):
        """Resolve and handle a request to given url"""
        handler, args, kwargs = self.find_handler(request)

        if handler.query is True:
            args += (request.query, )
        elif request.query:
            if isinstance(handler.query, str):
                kwargs[handler.query] = request.query.get(handler.query, None)
            elif isinstance(handler.query, (list, tuple, set)):
                for name in handler.query:
                    kwargs[name] = request.query.get(name, None)
            elif isinstance(handler.query, dict):
                for name, proxy in handler.query.items():
                    kwargs[proxy] = request.query.get(name, None)
        else:
            if not handler.query is False:
                raise exceptions.ControllerError

        return handler, args, kwargs

    def find_handler(self, request:dchttp.Request):
        """Resolve the appropriate handler for the given path and request method

         :return partial function encapsulating the handler function
         with arguments constructed form path, as well as *args and **kwargs
        """
        raise NotImplementedError


class TreePathMap(PathMap):
    """Hashmap tree based path mapper implementation"""
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
        console.cprint('Registering on path /' + path + '     Handler: ' + repr(handler))
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

    def find_handler(self, request):
        path = request.path.split('/')[1:] if request.path.startswith('/') else request.path.split('/')
        iargs, ikwargs = [], {}
        wildcard = getattr(self.wildcard, request.method) if self.wildcard is not None else None
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
                if new.wildcard and getattr(new.wildcard, request.method) is not None:
                    wildcard = functools.partial(getattr(new.wildcard, request.method), *iargs, **ikwargs)
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
                handler_func = getattr(handler, request.method)
            except AttributeError:
                raise AttributeError('Unrecognized Request method ' + repr(request.method))
            if not handler_func is None:
                return functools.partial(handler_func, *iargs, **ikwargs)


        if wildcard is None:
            raise exceptions.MethodHandlerNotFound('Mo handler found for request method ' + request.method + ' for path ' + request.path)
        else:
            return functools.partial(wildcard.func, *wildcard.args + (request.path, ), **wildcard.keywords)


class MultiTableSegment(Segment):
    """Special Subclass of segment used for the MultiMap path mapper"""
    def get_handler_container(self, path):
        first, *rest = path

        if rest:
            if first == '**':
                raise exceptions.ControllerError('Midsection cannot be wildcard')
            elif first in self:
                b = self[first]
                if isinstance(b, HandlerContainer):
                    b = self[first] = MultiTableSegment(first, b)
                elif not isinstance(b, MultiTableSegment):
                    raise exceptions.ControllerError('Expected Handler, or Segment, found ' + repr(type(b)))
            else:
                b = self[first] = MultiTableSegment(first)

            return b.get_handler_container(rest)
        else:
            if first == '**':
                if self.wildcard is None:
                    self.wildcard = HandlerContainer()
                a = self.wildcard
            else:
                a = self.setdefault(first, HandlerContainer())
            if isinstance(a, MultiTableSegment):
                if a.handler is None:
                    a.handler = HandlerContainer()

                a = a.handler
            return a

    def segment_get_handler(self, path:str, method):
        rest = collections.deque()
        p = '/' + path if not path.startswith('/') else path

        def rethandler_func(func):
            handler = func.handler if isinstance(func, MultiTableSegment) else func
            if getattr(handler, method) is None:
                raise exceptions.MethodHandlerNotFound(repr(handler))
            else:
                return getattr(handler, method)

        exception = None

        while p != '':
            if p in self:
                match = self[p]
                if rest:
                    try:
                        return match.segment_get_handler('/'.join(rest), method)
                    except (exceptions.PathResolving, exceptions.MethodHandlerNotFound) as e:
                        if exception is None:
                            exception = e
                else:
                    try:
                        return rethandler_func(match), ()
                    except exceptions.MethodHandlerNotFound as e:
                        if exception is None:
                            exception = e

            p, r = p.rsplit('/', 1)
            rest.appendleft(r)

        else:
            p, *rest = rest
            p, t = (int(p), int) if p.isnumeric() else (p, str)
            if t in self:
                match = self[t]
                if rest:
                    try:
                        func, args = match.segment_get_handler('/'.join(rest), method)
                        return func, (p, ) + args
                    except (exceptions.PathResolving, exceptions.MethodHandlerNotFound) as e:
                        if exception is None:
                            exception = e
                else:
                    try:
                        return rethandler_func(match), (p, )
                    except exceptions.MethodHandlerNotFound as e:
                        if exception is None:
                            exception = e
            if self.wildcard is not None:
                return rethandler_func(self.wildcard), (None, )
            else:
                raise exceptions.PathResolving('No matching path could be found for ' + path) \
                    if exception is None else exception


class MultiTablePathMap(MultiTableSegment, PathMap):
    """Path mapper implementation based on junction stacked hash tables"""
    @staticmethod
    def parse_path(path):
        """
        Split path into list of segments, parsed according to the path mapping minilanguage
         with the structure needed for incorporation into the MultiMap path mapper

        :param path:
        :return:
        """
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
                yield ''
            yield _inner(first)
            for a in rest:
                yield _inner(a)

        segments = split_segments(path)

        r = []
        p = []

        def flush_p():
            if p:
                if p[0] != '':
                    p.insert(0,'')
                r.append('/'.join(p))
                p.clear()

        for s in segments:
            if isinstance(s, str):
                if s == '**':
                    flush_p()
                    r.append(s)
                else:
                    p.append(s)
            elif isinstance(s, type) or isinstance(s, TypeArg):
                flush_p()
                r.append(s)
        else:
            flush_p()

        return r


    def add_path(self, path:str, handler):
        console.cprint('Registering on path /' + path + '     Handler: ' + repr(handler))
        path_list = self.parse_path(path)
        typeargs = tuple(filter(lambda a: isinstance(a, type) or isinstance(a, TypeArg) or a == '**', path_list))
        handler.typeargs = typeargs
        self.add_to_container(self.get_handler_container(path_list), handler)

    def find_handler(self, request):
        handler, typeargs = self.segment_get_handler(request.path, request.method)

        def process_args(typeargs, values):
            args = []
            kwargs = {}
            for targ, val in zip(typeargs, values):
                if targ == '**':
                    args.append(request.path)
                elif isinstance(targ, TypeArg):
                    kwargs[targ.name] = val
                elif isinstance(targ, type):
                    args.append(val)
                else:
                    raise TypeError('Expected Type ' + repr(type) + ' or ' + repr(TypeArg) + ' got ' + repr(type(targ)))

            return tuple(args), kwargs

        if handler.typeargs:
            args, kwargs = process_args(handler.typeargs, typeargs)

            return handler, args, kwargs

        return handler, (), {}


_component.Component('PathMap')(
    {
        'multitable': MultiTablePathMap,
        'tree': TreePathMap
    }[settings.PATHMAP_TYPE.lower()]
)