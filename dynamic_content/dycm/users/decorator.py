"""decorators of the users module"""
import functools
from dycm.users import users, model
from framework.util import structures, decorators
from framework.mvc import context
from framework.errors import exceptions

__author__ = 'Justus Adam'


def authorize(permission):
    """
    Decorates a controller_function/method to ensure authorization before
    executing the function

    :param permission: permission to require
    :return:
    """
    if not isinstance(permission, users.Permission):
        permission = users.Permission(permission)

    @context.apply_to_context(apply_before=True)
    def inner(dc_obj):
        if not permission.check(dc_obj.request.client.user):
            raise exceptions.LackingPermission(dc_obj.request.client.user, permission)

    return inner


def authorize_group(*groups):
    """
    Allow only provided groups access

    :param groups:
    :return:
    """
    def ensure_gid(group):
        if isinstance(group, model.AccessGroup):
            return group.oid
        elif not isinstance(group, int):
            raise TypeError
        return group

    groups = (ensure_gid(group) for group in groups)

    def wrap(func):
        @functools.wraps(func)
        @decorators.apply_to_type(structures.DynamicContent, apply_before=True)
        def inner(dc_obj):
            gid = dc_obj.request.client.user.access_group.oid
            if gid not in groups:
                raise exceptions.LackingPermission(
                    dc_obj.request.client.user,
                    '<group not authorized {}>'.format(gid)
                )

        return inner

    return wrap
