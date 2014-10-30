__author__ = 'justusadam'


class DynamicContentError(Exception):
    pass


class AuthorizationRequiredError(DynamicContentError):
    pass


class MissingPermissionError(DynamicContentError):
    pass


class MissingFileError(DynamicContentError):
    pass


class BackendUnreachableError(DynamicContentError):
    pass


class PageNotFoundError(DynamicContentError):
    pass


class InvalidInputError(DynamicContentError):
    pass


class AccessDisabled(DynamicContentError):
    pass


class UninitializedValueError(DynamicContentError):
    pass


class OverwriteProhibitedError(DynamicContentError):
    pass