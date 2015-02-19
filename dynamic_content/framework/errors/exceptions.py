__author__ = 'Justus Adam'
__version__ = '0.1'


class DCException(Exception):
    """Base Exception"""
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message

    __str__ = __repr__


class Vardump(DCException):
    """Perform a Vardump (PHP)"""
    def __init__(self, request, locals, globals):
        super().__init__('Dumping Variables')
        self.request = request
        self.locals = locals() if callable(locals) else locals
        self.globals = globals() if callable(globals) else globals


class ControllerError(DCException):
    """Controller related Errors"""
    pass


class UnexpectedControllerArgumentError(ControllerError):
    """A badly configured controller is being called with too many arguments"""
    pass


class PathResolving(ControllerError):
    """Path could not be resolved"""
    pass


class MethodHandlerNotFound(ControllerError):
    """This path exists but does not cater to this request method"""
    pass


class PathNotFound(ControllerError):
    """Basically 404"""
    pass


class ComponentError(DCException):
    """Component related exceptions"""
    pass


class ComponentNotLoaded(ControllerError):
    """Trying to access a non existent component"""
    def __init__(self, name):
        super().__init__('Component ' + name + ' is not loaded.')


class ComponentLoaded(ControllerError):
    """Assigning to a non-assignable component"""
    def __init__(self, name):
        super().__init__('Component ' + name + ' is already loaded.')


class HookExists(DCException):
    """A previously initialized hook is being initialized again"""

    def __init__(self, hook):
        super().__init__('{} already exists'.format(hook))


class HookNotInitialized(DCException):
    """
    A hook that has not been initialized is being assigned to
    """
    def __init__(self, hook):
        super().__init__('{} hooks are not initalized'.format(hook))


class LackingPermission(DCException):
    """
    A client lacks a required permission for an action.
    """
    def __init__(self, client, permission, action=''):
        super().__init__(
            'User "{}" does not have permission "{}"'
            ' required for this action {}'.format(client, permission, action)
        )
        self.client = client
        self.permission = permission
        self.action = action


class LinkerException(DCException):
    """Base exception for errors with links"""
    pass


class LinkingException(LinkerException):
    """Base exception for errors while linking"""
    def __init__(self, link, nested_exception=None, message=None):
        s = ['{} in link {}'.format(self.__class__.__name__, link)]
        if isinstance(nested_exception, Exception):
            s.append('with nested exception: {}'.format(nested_exception))
        if message is not None:
            s.append('with message {}'.format(message))
        super().__init__(
            ' '.join(s)
        )


class LinkingFailed(LinkingException):
    """Attempting to link failed"""
    pass


class UnlinkingFailed(LinkingException):
    """Attempting to unlink failed"""
    pass


class IsLinked(LinkerException):
    """Trying to link a already linked link"""
    def __init__(self, link):
        super().__init__('{} has been linked already'.format(link))


class IsNotLinked(LinkerException):
    """trying to unlink an unliked link"""
    def __init__(self, link):
        super().__init__('{} is not linked'.format(link))
