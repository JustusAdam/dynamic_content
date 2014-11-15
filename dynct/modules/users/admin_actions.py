import re
import copy
from urllib.error import HTTPError

from dynct.core.mvc.content_compiler import Content
from dynct.modules.comp.html_elements import TableElement, Input, ContainerElement, Label, Checkbox, TableRow, TableData
from . import users
from dynct.modules.form.secure import SecureForm
from dynct.modules.users.user_information import UsersOverview
from .user_information import UserInformation
from . import ar


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
        return UsersOverview
    handlers = {
        'edit': EditUser,
        'overview': UsersOverview,
        'show': UserInformation
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


class CreateUser(Content):
    page_title = 'Create User'
    destination = '/'
    message = ''
    permission = 'edit user accounts'
    published = True
    theme = 'admin_theme'

    def __init__(self, url, client):
        super().__init__(client)
        self.url = url

    def process_content(self):

        return ContainerElement(
            self.message, self.user_form())

    def target_url(self):
        if 'destination' in self.url.get_query:
            target_url = str(self.url)
        else:
            target_url = str(self.url) + '?destination=' + self.destination + ''
        return target_url

    def user_form(self, **kwargs):
        acc = []
        for (display_name, name) in _edit_user_table_order:
            arguments = {}
            if name in _edit_user_form:
                arguments = _edit_user_form[name]
            if name in kwargs:
                arguments['value'] = kwargs[name]
            acc.append([Label(display_name, label_for=name), Input(name=name, **arguments)])

        return SecureForm(
            TableElement(
                *acc
            ), action=self.target_url(), element_id='admin_form'
        )

    def _process_post(self):
        if 'password' in self.url.post:
            if self.url.post['confirm-password'] != self.url.post['password']:
                self.message = ContainerElement('Your passwords did not match.', classes={'alert'})
                return
        args = dict()
        for key in ['username', 'password', 'email', 'last_name', 'first_name', 'middle_name']:
            if key in self.url.post:
                args[key] = self.url.post[key][0]
        self.action(**args)
        self.redirect(str(self.url.path))

    def compile(self):
        if self.url.post:
            self._process_post()
        return super().compile()


    def action(self, **kwargs):
        users.add_user(**kwargs)

    def redirect(self, destination=None):
        if 'destination' in self.url.get_query:
            destination = self.url.get_query['destination'][0]
        elif not destination:
            destination = str(self.url.path.prt_to_str(0, -1))
        raise HTTPError(str(self.url), 302, 'Redirect',
                        {('Location', destination), ('Connection', 'close')}, None)


class EditUser(CreateUser):
    page_title = 'Edit User'
    destination = '/'
    message = ''

    def action(self, **kwargs):
        users.edit_user(self.url.page_id, **kwargs)

    def user_form(self, **kwargs):
        (user_id, username, email, first_name, middle_name, last_name, date_created) = users.get_single_user(
            self.url.page_id)
        return super().user_form(user_id=user_id,
                                 username=username,
                                 email=email,
                                 first_name=first_name,
                                 middle_name=middle_name,
                                 last_name=last_name,
                                 date_created=date_created)


class PermissionOverview(Content):
    page_title = 'Permissions Overview'
    permission = 'view permissions'
    _perm_list = None
    theme = 'admin_theme'

    def __init__(self, url, client):
        super().__init__(client)

    def process_content(self):
        return ContainerElement(
            ContainerElement(
                'Please note, that permissions assigned to the group \'any authorized user\' automatically apply to any other group as well as any authenticated user',
                classes={'alert'}), self.permission_table()
        )

    def permission_table(self):
        l = self.compile_the_list()
        return TableElement(
            *[
                TableRow(
                    *[
                         TableData(a[0], classes=_permission_table_permissions_classes)
                     ] + [
                        TableData(b, classes=_permission_table_boolean_classes) for b in a[1:]
                    ]
                )
                for a in l
            ], classes=_permission_table_classes
        )

    @property
    def permissions_list(self):
        if not self._perm_list:
            l = [(a.aid, a.permission) for a in ar.AccessGroupPermission.get_all()]
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
        l = []
        access_groups = sorted(ar.AccessGroup.get_all(), key=lambda a: a.aid)
        l.append(['Permissions'] + [a.machine_name for a in access_groups])
        permissions = {}
        for aid, per in self.permissions_list:
            if per in permissions:
                permissions[per].append(aid)
            else:
                permissions[per] = [aid]

        for p in permissions:
            row = sorted(permissions[p])
            l.append([p] + list(
                map(lambda a: self.checkbox(a.aid in row, '-'.join([str(a.aid), p.replace(' ', '-')])), access_groups)))
        l.sort(key=lambda a: a[0])
        return l

    def checkbox(self, value, name):
        return {True: '&#x2713;', False: ''}[value]


permission_structure = re.compile('(\d)+-([0-9a-zA-Z_-]+)')


class EditPermissions(PermissionOverview):
    page_title = 'Edit Permissions'
    permission = 'edit permissions'

    def __init__(self, url, client):
        super().__init__(url, client)
        self.url = url

    def compile(self):
        if self.url.post:
            self._process_post()
        return super().compile()

    def permission_table(self):
        return SecureForm(
            super().permission_table()
            , action=str(self.url.path)
        )

    def checkbox(self, value, name):
        return Checkbox(name=name, value=name, checked=value)

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


class AccGrpOverview(Content):
    page_title = 'Access Groups Overview'
    permission = 'view access groups'


class EditAccGrp(AccGrpOverview):
    page_title = 'Edit Access Groups'
    permission = 'edit access groups'