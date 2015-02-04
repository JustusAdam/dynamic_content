import re
import itertools

from dycc import route
from dycc import http
from dycc.util import html
from dycc.middleware import csrf
from dycm import theming
from dycm.users import model, users, decorator


__author__ = 'Justus Adam'

_edit_user_form = {
    'password': {
        'input_type': 'password',
        'required': True
    },
    'confirm-password': {
        'input_type': 'password',
        'required': True
    },
    'email': {
        'input_type': 'email',
        'required': True
    },
    'username': {
        'required': True
    }
}

_edit_user_table_order = [
    ('First name', 'first_name'),
    ('Name', 'last_name'),
    ('Middle name', 'middle_name'),
    ('Username', 'username'),
    ('Email-Address', 'email'),
    ('Password', 'password'),
    ('Confirm Password', 'confirm-password')
]

_permission_table_classes = {'admin-table', 'permission-table'}

_permission_table_permissions_classes = {'permission-name'}

_permission_table_boolean_classes = {'permission-boolean'}


def split_list(l, func):
    true = []
    false = []
    for i in l:
        if func(i):
            true.append(i)
        else:
            false.append(i)
    return true, false


def user_form(**values):
    for (display_name, name) in _edit_user_table_order:
        kwargs = _edit_user_form.get(name, {})
        kwargs.__setitem__('value', values[name]) if name in values else None
        yield html.Label(display_name, label_for=name), html.Input(name=name, **kwargs)


@route.controller_function('users/new', method=http.RequestMethods.GET, query=False)
@decorator.authorize('edit user accounts')
@theming.theme(default_theme='admin_theme')
def create_user_form(dc_obj):

    dc_obj.context['title'] = 'Create User'
    dc_obj.context['content'] = csrf.SecureForm(
        html.TableElement(
            *tuple(user_form())
        ), action='/users/new', element_id='admin_form'
    )
    return 'user_overview'


@route.controller_function('users/new', method=http.RequestMethods.POST, query=True)
@decorator.authorize('edit user accounts')
def create_user_action(dc_obj, post):
    if 'password' in post:
        if post['confirm-password'] != post['password']:
            dc_obj.context['title'] = 'Passwords do not match'
            dc_obj.context['content'] = ''
            return 'error'
        else:
            args = post_to_args(post)
            u = users.add_user(**args)
            return ':redirect:/users/' + str(u.oid)


post_to_args = lambda post: {
        key: post[key][0] for key in (
            'username', 'password', 'email', 'last_name', 'first_name', 'middle_name'
        ) if key in post
    }


@route.controller_function(
    'users/{int}/edit',
    method=http.RequestMethods.POST,
    query=True
    )
def edit_user_action(model, uid, post):
    args = post_to_args(post)
    users.edit_user(uid, **args)

    return ':redirect:/'


@route.controller_function(
    'users/{int}/edit',
    method=http.RequestMethods.GET,
    query=False
    )
@theming.theme(default_theme='admin_theme')
def edit_user_form(dc_obj, uid):
    dc_obj.context['title'] = 'Edit User'

    user = users.get_single_user(int(uid))
    uf = user_form(
        user_id=user.oid,
        username=user.username,
        email=user.email_address,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        date_created=user.date_created
        )
    dc_obj.context['content'] = csrf.SecureForm(*tuple(itertools.chain(*uf)))
    return 'user_overview'


def _sort_perm_list(l):
    l.sort(key=lambda a: a[1])
    l.sort(key=lambda a: a[0])
    return l


def compile_permission_list(permissions_list, checkbox_hook):
    access_groups = sorted(model.AccessGroup.select(), key=lambda a: a.oid)

    def _list():
        yield ('Permissions', ) + tuple(a.machine_name for a in access_groups)
        permissions = {}
        for aid, per in permissions_list:
            if per in permissions:
                permissions[per].append(aid)
            else:
                permissions[per] = [aid]

        for p in permissions:
            row = sorted(permissions[p])
            yield [p] + list(
                map(
                    lambda a: checkbox_hook(
                        a.oid in row,
                        '{}-{}'.format(a.oid, p.replace(' ', '-'))
                        ),
                    access_groups
                    )
                )

    return sorted(_list(), key=lambda a: a[0])


def permission_table(checkbox):
    perms = model.AccessGroupPermission.select()
    sort_perms = _sort_perm_list([(a.group.oid, a.permission) for a in perms])
    comp_perms = compile_permission_list(sort_perms, checkbox)

    return html.TableElement(
        *tuple(
            html.TableRow(
                html.TableData(a[0], classes=_permission_table_permissions_classes),
                *tuple(
                    html.TableData(b, classes=_permission_table_boolean_classes)
                    for b in a[1:]
                    )
                )
            for a in comp_perms
            ),
        classes=_permission_table_classes
        )


@route.controller_function(
    'users/permissions',
    method=http.RequestMethods.GET,
    query=False
    )
@decorator.authorize('view permissions')
@theming.theme(default_theme='admin_theme')
def permission_overview(dc_obj):
    dc_obj.context['title'] = 'Permissions Overview'

    table = permission_table(lambda a, b: '&#x2713;' if a else '')

    dc_obj.context['content'] = html.ContainerElement(
        html.ContainerElement(
            'Please note, that permissions assigned to the group \'any'
            ' authorized user\' automatically apply to any other group'
            ' as well as any authenticated user',
            classes={'alert'}), table
    )
    return 'user_overview'


permission_structure = re.compile('^(\d)+-([0-9a-zA-Z_-]+)$')


@route.controller_function(
    'users/permissions/edit',
    method=http.RequestMethods.GET,
    query=False
    )
@decorator.authorize('edit permissions')
@theming.theme(default_theme='admin_theme')
def edit_permissions(dc_obj):
    dc_obj.context['title'] = 'Edit Permissions'
    dc_obj.context['content'] = csrf.SecureForm(
        permission_table(
            lambda value, name: html.Checkbox(name=name, value=name, checked=value)
        ),
        action='/users/permissions/edit'
    )
    return 'user_overview'


@route.controller_function(
    'users/permissions/edit',
    method=http.RequestMethods.POST,
    query=True
    )
@decorator.authorize('edit permissions')
def edit_permissions_action(dc_obj, post):
    permissions_list = _sort_perm_list([(a.group.oid, a.permission) for a in model.AccessGroupPermission.select()])
    new_perm = []
    for item in post:
        m = re.match(permission_structure, item)
        if m:
            g = m.groups()
            # print('assigning permission ' + ' '.join([g[1].replace('-', ' '), 'to', str(g[0])]))
            new_perm.append((int(g[0]), g[1].replace('-', ' ')))
    new_perm = _sort_perm_list(new_perm)
    old_perm, control_perm = split_list(permissions_list, lambda a: int(a[0]) != users.CONTROL_GROUP, )
    add = []
    remove = []
    while new_perm and old_perm:
        i = new_perm.pop()
        j = old_perm.pop()
        if not i == j:
            if i in old_perm:
                old_perm.remove(i)
            else:
                add.append(i)

            if j in new_perm:
                new_perm.remove(j)
            else:
                remove.append(j)
    if new_perm:
        add += new_perm
    if old_perm:
        remove += old_perm

    for aid, permission in remove:
        users.revoke_permission(aid, permission)
    for aid, permission in add:
        users.assign_permission(aid, permission)

    return ':redirect:/users/permissions'
