from functools import wraps
from dynct.core.mvc.model import Model
from dynct.util.decorators import apply_to_type

__author__ = 'justusadam'


def authorize(permission):
    def wrap(func):
        @wraps(func)
        @apply_to_type(Model, apply_before=True)
        def inner(model):
            if not model.client.check_permission(permission):
                raise PermissionError

        return inner

    return wrap


def authorize_group(group):
    def wrap(func):
        @wraps(func)
        @apply_to_type(Model, apply_before=True)
        def inner(model):
            pass

        return inner

    return wrap