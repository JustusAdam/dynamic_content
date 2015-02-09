__author__ = 'Justus Adam'
__version__ = '0.1'


class DCException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message

    __str__ = __repr__


class Vardump(DCException):
    def __init__(self, request, locals, globals):
        super().__init__('Dumping Variables')
        self.request = request
        self.locals = locals() if callable(locals) else locals
        self.globals = globals() if callable(globals) else globals


class ControllerError(DCException):
    pass


class UnexpectedControllerArgumentError(ControllerError):
    pass


class PathResolving(ControllerError):
    pass


class MethodHandlerNotFound(ControllerError):
    pass


class PathNotFound(ControllerError):
    pass


class ComponentError(DCException):
    pass


class ComponentNotLoaded(ControllerError):
    def __init__(self, name):
        super().__init__('Component ' + name + ' is not loaded.')


class ComponentLoaded(ControllerError):
    def __init__(self, name):
        super().__init__('Component ' + name + ' is already loaded.')


class HookExists(DCException):
    def __init__(self, hook):
        super().__init__('{} already exists'.format(hook))


class HookNotInitialized(DCException):
    def __init__(self, hook):
        super().__init__('{} hooks are not initalized'.format(hook))


class LackingPermission(DCException):
    def __init__(self, client, permission, action=''):
        super().__init__(
            'User "{}" does not have permission "{}"'
            ' required for this action {}'.format(client, permission, action)
        )
        self.client = client
        self.permission = permission
        self.action = action