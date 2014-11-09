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
    def __init__(self, attribute:str=None, expected:str=None, received:str=None):
        self.attribute = attribute
        self.expected = expected
        self.received = received

    def __str__(self):
        acc = [self.__class__.__name__ + ':', 'invalid value']
        if self.attribute:
            acc.append('for attribute ' + str(self.attribute))
        if self.expected:
            acc.append(str(self.expected) + ' was expected')
        if self.received:
            acc.append('received ' + str(self.received))
        return ' '.join(acc)


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