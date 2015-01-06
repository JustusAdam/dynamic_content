__author__ = 'Justus Adam'
__version__ = '0.1'


class DCException(Exception):
    pass


class ControllerError(DCException):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message

    __str__ = __repr__


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
