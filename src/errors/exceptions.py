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


class UninitializedValueError(DynamicContentError):
    pass


class OverwriteProhibitedError(DynamicContentError):
    def __init__(self, attribute_or_key, value):
        self.key = attribute_or_key
        self.value = value

    def __str__(self):
        super().__str__() + '\n ({}, {})'.format(str(self.key), str(self.value))
