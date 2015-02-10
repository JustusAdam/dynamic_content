import functools
from framework.util import structures, decorators
from framework.mvc import context
from framework.errors import exceptions

__author__ = 'Justus Adam'


def authorize(permission):
    @context.apply_to_context(apply_before=True)
    def inner(model):
        if not model.request.client.check_permission(permission):
            raise exceptions.LackingPermission(model.request.client.user, permission)

    return inner


def authorize_group(group):
    def wrap(func):
        @functools.wraps(func)
        @decorators.apply_to_type(structures.DynamicContent, apply_before=True)
        def inner(model):
            pass

        return inner

    return wrap
