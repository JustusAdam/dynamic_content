__author__ = 'justus2'


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