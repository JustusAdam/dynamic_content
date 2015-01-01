__author__ = 'justusadam'


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