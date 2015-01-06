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
        def _compare_two(one, other):
            if one.headers == other.headers:
                raise exceptions.ControllerError(
                'Handler mapping collision. Headers do not differ.')

        for a in handler_func.method:
            current = getattr(container, a)
            if current is None:
                setattr(container, a, handler_func)
            elif isinstance(current, tuple):
                for item in current:
                    _compare_two(item, handler_func)
                else:
                    setattr(container, a,
                        sorted((handler_func, ) + current, key=len))
            else:
                _compare_two(current, handler_func)
                setattr(container, a, sorted((handler_func, current), key=len))


TypeArg = collections.namedtuple('TypeArg', ('name', 'type'))
# A Path argument with a name.

class HandlerContainer(object):
    """Value object for holding handlers to various request types with some convenience methods for value access"""

    __slots__ = ('get', 'post')

    def __init__(self, get=None, post=None):
        self.get = get
        self.post = post


typemap = {
    'int': int,
    'str': str,
    'integer': int,
    'string': str,
    'float': float
}


def handler_from_container(container, method, headers):
    handler = getattr(
        (container.handler
            if isinstance(container, Segment)
            else container),
        method)
    if handler is not None:
        if isinstance(handler, tuple):
            pass
            # TODO match headers
        else:
            return handler
    else:
        return None


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
            elif isinstance(handler.query, (list, tuple, set, frozenset)):
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
        console.cprint('Registering on path /{}     Handler: {}'.format(handler, handler))
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
                raise TypeError('Expected Type {} or {} not {}'.format(str, type, type(segment)))

            if not isinstance(new, Segment):
                if isinstance(segment, str):
                    new = old[segment] = Segment(segment, new)
                elif isinstance(segment, type):
                    new = old[segment] = Segment(None, new)
                elif isinstance(segment, TypeArg):
                    new = old[segment.type] = Segment(segment.name, new)
                else:
                    raise TypeError('Expected Type {} or {} not {}'.format(str, type, type(segment)))
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
        wildcard = (getattr(self.wildcard, request.method), (), {}) if self.wildcard is not None else None
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
                raise TypeError('Expected type {} got {!s}'.format(str, type(segment)))
            try:
                return old[segment]
            except KeyError:
                t = int if segment.isnumeric() else str
                return handle_type(segment, t)

        new = segment_chain[-1]
        for segment in path:
            if isinstance(new, Segment):
                if new.wildcard and getattr(new.wildcard, request.method) is not None:
                    wildcard = getattr(new.wildcard, request.method), tuple(iargs), ikwargs
            else:
                break

            try:
                new = get_new(segment_chain[-1], segment)
            except exceptions.PathNotFound:
                break
            segment_chain.append(new)


        else:
            handler = handler_from_container(new, request.method, request.headers)
            if not handler is None:
                return handler, iargs, ikwargs


        if wildcard is None:
            raise exceptions.MethodHandlerNotFound(
            'Mo handler found for request method {} for path {}'.format(
            request.method, request.path))
        else:
            handler, args, kwargs = wildcard
            return handler, args + (request.path, ), kwargs


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
                    raise exceptions.ControllerError('Expected Handler, or Segment, found {}'.format(type(b)))
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

    def segment_get_handler(self, path, method, headers):
        rest = collections.deque()
        p = '/' + path if not path.startswith('/') else path

        def rethandler_func(container):
            handler = handler_from_container(container, method, headers)
            if handler is None:
                raise exceptions.MethodHandlerNotFound(repr(handler))
            else:
                return handler

        exception = None

        while p != '':
            if p in self:
                match = self[p]
                if rest:
                    try:
                        return match.segment_get_handler('/'.join(rest), method, headers)
                    except (exceptions.PathResolving,
                        exceptions.MethodHandlerNotFound) as e:
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
                        func, args = match.segment_get_handler('/'.join(rest), method, headers)
                        return func, (p, ) + args
                    except (exceptions.PathResolving,
                        exceptions.MethodHandlerNotFound) as e:
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
                raise (exceptions.PathResolving(
                    'No matching path could be found for {}'.format(path))
                    if exception is None else exception)


class MultiTablePathMap(MultiTableSegment, PathMap):
    """Path mapper implementation based on junction stacked hash tables"""
    @staticmethod
    def parse_path(path):
        """
        Split path into list of segments, parsed according to the
         path mapping minilanguage with the structure needed for
         incorporation into the MultiMap path mapper

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
        console.cprint('Registering on path /{}     Handler: {}'.format(
            path, handler))
        path_list = self.parse_path(path)
        typeargs = tuple(filter(lambda a: (isinstance(a, type)
            or isinstance(a, TypeArg) or a == '**'), path_list))
        handler.typeargs = typeargs
        self.add_to_container(self.get_handler_container(path_list), handler)

    def find_handler(self, request):
        # TODO add headers to request and pass them on in this call
        handler, typeargs = self.segment_get_handler(request.path, request.method, None)

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
                    raise TypeError('Expected Type {} or {} got {}'.format(type,
                        TypeArg, type(targ)))

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
