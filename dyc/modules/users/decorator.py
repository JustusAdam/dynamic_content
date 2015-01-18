from functools import wraps
from dyc.core.mvc.context import Context
from dyc.util.decorators import apply_to_type
from dyc.errors import exceptions

__author__ = 'Justus Adam'


def authorize(permission):
    @apply_to_type(Context, apply_before=True)
    def inner(model):
        if not model.client.check_permission(permission):
            raise exceptions.LackingPermission(model.client, permission)

    return inner


def authorize_group(group):
    def wrap(func):
        @wraps(func)
        @apply_to_type(Context, apply_before=True)
        def inner(model):
            pass

        return inner

    return wrap