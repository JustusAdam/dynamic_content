import re
import copy

from dynct.core.mvc import content_compiler as _cc, decorator as mvc_dec
from dynct.modules.comp import html
from dynct.modules import form
from . import user_information as uinf, model, users


__author__ = 'justusadam'

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


def factory(url):
    if url.page_id == 0:
        if url.page_modifier == 'new':
            return CreateUser
    handlers = {
        'edit': EditUser,
        'overview': uinf.UsersOverview,
        'show': uinf.UserInformation
    }
    return handlers[url.page_modifier]


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
        yield [html.Label(display_name, label_for=name), html.Input(name=name, **kwargs)]


@mvc_dec.controller_function('users', '/new', get=False, post=False)
def create_user_form(model):
    if not model.client.check_permission('edit user accounts'):
        return 'error'

    model.theme = 'admin_theme'
    model['title'] = 'Create User'
    model['content'] = form.SecureForm(
            html.TableElement(
                *list(user_form())
            ), action='/users/new', element_id='admin_form'
        )
    return 'page'


@mvc_dec.controller_function('users', '/new', get=False, post=True)
def create_user_action(model, post):
    if 'password' in post:
        if post['confirm-password'] != post['password']:
            return 'error'
        else:
            args = {
                key: post[key][0] for key in [
                   'username', 'password', 'email', 'last_name', 'first_name', 'middle_name'
                ] if key in post
            }
            u = users.add_user(**args)
            return ':redirect:/users/' + str(u.oid)


@mvc_dec.controller_function('users', '/([0-9]+0)/edit', get=False, post=True)
def edit_user_action(model, uid, post):
    args = {
                key: post[key][0] for key in [
                   'username', 'password', 'email', 'last_name', 'first_name', 'middle_name'
                ] if key in post
            }
    users.edit_user(uid, **args)

    return ':redirect:/'


@mvc_dec.controller_function('users', '/([0-9]+)/edit', get=False, post=False)
def edit_user_form(model, uid):
    model['title'] = 'Edit User'

    (user_id, username, email, first_name, middle_name, last_name, date_created) = users.get_single_user(
        int(uid))
    uf = user_form(user_id=user_id,
                 username=username,
                 email=email,
                 first_name=first_name,
                 middle_name=middle_name,
                 last_name=last_name,
                 date_created=date_created)
    model.theme = 'admin_theme'
    model['content'] = uf
    return 'page'


class PermissionOverview(_cc.Content):
    page_title = 'Permissions Overview'
    permission = 'view permissions'
    _perm_list = None
    theme = 'admin_theme'

    def process_content(self):
        return html.ContainerElement(
            html.ContainerElement(
                'Please note, that permissions assigned to the group \'any authorized user\' automatically apply to any other group as well as any authenticated user',
                classes={'alert'}), self.permission_table()
        )

    def permission_table(self):
        l = self.compile_the_list()
        return html.TableElement(
            *[
                html.TableRow(
                    *[
                         html.TableData(a[0], classes=_permission_table_permissions_classes)
                     ] + [
                        html.TableData(b, classes=_permission_table_boolean_classes) for b in a[1:]
                    ]
                )
                for a in l
            ], classes=_permission_table_classes
        )

    @property
    def permissions_list(self):
        if not self._perm_list:
            l = [(a.aid, a.permission) for a in model.AccessGroupPermission.get_all()]
            self._perm_list = self._sort_perm_list(l)
        return self._perm_list

    @permissions_list.setter
    def permissions_list(self, val):
        self._perm_list = val

    def _sort_perm_list(self, l):
        l.sort(key=lambda a: a[1])
        l.sort(key=lambda a: a[0])
        return l

    def compile_the_list(self):
        access_groups = sorted(model.AccessGroup.get_all(), key=lambda a: a.aid)

        def _list():
            yield ['Permissions'] + [a.machine_name for a in access_groups]
            permissions = {}
            for aid, per in self.permissions_list:
                if per in permissions:
                    permissions[per].append(aid)
                else:
                    permissions[per] = [aid]

            for p in permissions:
                row = sorted(permissions[p])
                yield [p] + list(
                    map(lambda a: self.checkbox(a.aid in row, '-'.join([str(a.aid), p.replace(' ', '-')])), access_groups))

        return sorted(_list(), key=lambda a: a[0])

    def checkbox(self, value, name):
        return {True: '&#x2713;', False: ''}[value]


permission_structure = re.compile('(\d)+-([0-9a-zA-Z_-]+)')


class EditPermissions(PermissionOverview):
    page_title = 'Edit Permissions'
    permission = 'edit permissions'

    def __init__(self, model, url):
        super().__init__(model)
        self.url = url

    def compile(self):
        if self.url.post:
            self._process_post()
        return super().compile()

    def permission_table(self):
        return form.SecureForm(
            super().permission_table()
            , action=str(self.url.path)
        )

    def checkbox(self, value, name):
        return html.Checkbox(name=name, value=name, checked=value)

    def _process_post(self):
        new_perm = []
        for item in self.url.post:
            m = re.fullmatch(permission_structure, item)
            if m:
                g = m.groups()
                # print('assigning permission ' + ' '.join([g[1].replace('-', ' '), 'to', str(g[0])]))
                new_perm.append((int(g[0]), g[1].replace('-', ' ')))
        new_perm = self._sort_perm_list(new_perm)
        old_perm, control_perm = split_list(self.permissions_list, lambda a: int(a[0]) != users.CONTROL_GROUP, )
        self.permissions_list = copy.copy(new_perm) + control_perm
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


class AccGrpOverview(_cc.Content):
    page_title = 'Access Groups Overview'
    permission = 'view access groups'


class EditAccGrp(AccGrpOverview):
    page_title = 'Edit Access Groups'
    permission = 'edit access groups'