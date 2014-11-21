from urllib.error import HTTPError
import re
import inspect

from dynct.errors import OverwriteProhibitedError, InvalidInputError


__author__ = 'justusadam'


_register_controllers = True


def parse_with(regex):
    def wrap(func):
        def w(self, url, client):
            return func(self, *re.match(regex, url).groups())
        return w
    return wrap


def authorize(permission):
    pass




def url_args(regex, *, get=False, post=False, strict:bool=False):
    """
    Function decorator for controller Methods. Parses the Input (url) without prefix according to the regex.
    Unpacks groups into function call arguments.

    get and post can be lists of arguments which will be passed to the function as keyword arguments or booleans
    if get/post are true the entire query is passed to the function as keyword argument 'get' or 'post'
    if get/post are false no queries will passed

    if strict is true, only specified values will be accepted,
    and the existence of additional arguments will cause an error.

    :param regex: regex pattern or string
    :param get: list/tuple (subclasses) or boolean
    :param post: list/tuple (subclasses) or boolean
    :param strict: boolean
    :return:
    """

    def q_comp(q, name):
        if type(q) == bool:
            if q:
                return lambda a:{name:a}
            elif strict:
                return lambda a: bool(a) if False else {}
            else:
                return lambda a: {}
                # return lambda a:{True: False, False:{}}[bool(a)]
        elif issubclass(type(q), (list,tuple)):
            if strict:
                def f(a:list, b:dict):
                    d = b.copy()
                    for item in a:
                        if item not in d:
                            raise InvalidInputError
                    return d
                return lambda a: len(q) == len(a.keys()) if f(q, a) else False
            return lambda a: {arg:a.get(arg) for arg in q}
        else:
            raise InvalidInputError

    get_func = q_comp(get, 'get')
    post_func = q_comp(post, 'post')

    def wrap(func):
        def _generic(url, client):
            kwargs = dict(client=client)
            for result in [get_func(url.get_query), post_func(url.post)]:
                if result is False:
                    raise InvalidInputError
                else:
                    kwargs.update(result)
            return re.match(regex, str(url.path)).groups(), kwargs
            # return (model, ) + re.match(regex, str(url.path)).groups(), kwargs
        def _method(self, url, client):
            args, kwargs = _generic(url, client)
            return func(self, *args, **kwargs)
        def _function(url, client):
            args, kwargs = _generic(url, client)
            return func(*args, **kwargs)
        if inspect.ismethod(func):
            return _method
        elif inspect.isfunction(func):
            return _function
        else:
            raise InvalidInputError
    return wrap



class Controller(dict):

    @parse_with('(\w*)/(\w)')
    def test(self, arg1, arg2):
        print(arg1)
        print(arg2)


class RegexURLMapper(Controller):
    pass



class ControllerMapper(dict):

    def register_modules(self):
        from dynct.core import Modules
        for l in Modules.get_handlers_by_class(Controller).values():
            for c in l:
                self.register_controller(c)

    def register_controller(self, controller_class):
        print(controller_class)
        instance = controller_class()
        if _register_controllers:
            if not hasattr(self, '_controller_classes'):
                self._controller_classes = []
            if not controller_class in self._controller_classes:
                self._controller_classes.append(controller_class)
            if not hasattr(self, '_controller_instances'):
                self._controller_instances = []
            self._controller_instances.append(instance)

        for key, value in instance.items():
            self[key] = value

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        if key in self:
            raise OverwriteProhibitedError
        super().__setitem__(key, value)

    def __call__(self, url):
        if url.path[0] in self:
            return self[url.path[0]]
        else:
            raise HTTPError(str(url), 404, None, None, None)