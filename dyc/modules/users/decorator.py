from functools import wraps
from dyc.core.mvc.model import Model
from dyc.util.decorators import apply_to_type

__author__ = 'Justus Adam'


def authorize(permission):
    @apply_to_type(Model, apply_before=True)
    def inner(model):
        if not model.client.check_permission(permission):
            raise PermissionError

    return inner


def authorize_group(group):
    def wrap(func):
        @wraps(func)
        @apply_to_type(Model, apply_before=True)
        def inner(model):
            pass

        return inner

    return wrap