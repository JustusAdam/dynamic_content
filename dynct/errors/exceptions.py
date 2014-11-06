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


class ModuleError(DynamicContentError):
    def __init__(self, module_name):
        self.module_name = module_name


class ModuleNotFoundError(ModuleError):
    def __repr__(self):
        return 'ModuleNotFoundError, module ' + self.module_name + ' could not be found in the Database'


class BackendError(DynamicContentError):
    pass


class DatabaseError(BackendError):
    pass


class DatabaseUnreachableError(DatabaseError):
    pass