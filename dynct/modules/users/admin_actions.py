from dynct.core.handlers.content import Content
from dynct.core.handlers.base import RedirectMixIn
from dynct.core.mvc.controller import Controller
from dynct.modules.comp.html_elements import TableElement, Input, ContainerElement, Label, Checkbox
from . import users
from dynct.modules.form.secure import SecureForm
from .user_information import UserInformation
import re
import copy

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


class CreateUser(Content, RedirectMixIn):
    page_title = 'Create User'
    destination = '/'
    message = ''
    permission = 'edit user accounts'
    published = True

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
                self.message = ContainerElement('Your passwords did not match.', classes='alert')
                return
        args = dict()
        for key in ['username', 'password', 'email', 'last_name', 'first_name', 'middle_name']:
            if key in self.url.post:
                args[key] = self.url.post[key][0]
        self.action(**args)
        self.redirect(str(self.url.path))


    def action(self, **kwargs):
        users.add_user(**kwargs)


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


class UsersOverview(Content):
    page_title = 'User Overview'
    permission = 'access users overview'

    def process_content(self):
        if 'selection' in self.url.get_query:
            selection = self.url.get_query['selection'][0]
        else:
            selection = '0,50'
        all_users = users.get_info(selection)
        acc = [['UID', 'Username', 'Name (if provided)', 'Date created', 'Actions']]

        for (user_id, username, user_first_name, user_middle_name, user_last_name, date_created) in all_users:
            acc.append([ContainerElement(str(user_id), html_type='a', additionals={'href': '/users/' + str(user_id)}),
                        ContainerElement(username, html_type='a', additionals={'href': '/users/' + str(user_id)}),
                        ' '.join([user_first_name, user_middle_name, user_last_name]),
                        date_created,
                        ContainerElement('edit', html_type='a',
                                         additionals={'href': '/users/' + str(user_id) + '/edit'})])

        if len(acc) == 1 or acc == []:
            return ContainerElement(ContainerElement('It seems you do not have any users yet.',
                                                     additionals={'style': 'padding:10px;text-align:center;'}),
                                    ContainerElement('Would you like to ', ContainerElement('create one', html_type='a',
                                                                                            additionals={
                                                                                            'href': '/users/new',
                                                                                            'style': 'color:rgb(255, 199, 37);text-decoration:none;'}),
                                                     '?', additionals={'style': 'padding:10px;'}), additionals={
                'style': 'padding:15px; text-align:center; background-color: cornflowerblue;color:white;border-radius:20px;font-size:20px;'})
        return TableElement(*acc, classes={'user-overview'})


class PermissionOverview(Content):
    page_title = 'Permissions Overview'
    permission = 'view permissions'
    _perm_list = None

    def process_content(self):
        return ContainerElement(
            ContainerElement('Please note, that permissions assigned to the group \'any authorized user\' automatically apply to any other group as well as any authenticated user', classes={'alert'}), self.permission_table()
            )

    def permission_table(self):
        return TableElement(*self.compile_the_list())

    @property
    def permissions_list(self):
        if not self._perm_list:
            l = self._get_permissions()
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
        access_groups = sorted([a for a in self.get_acc_groups()], key=lambda a: a[0])
        l.append(['Permissions'] + [a[1] for a in access_groups])
        permissions = {}
        for aid, per in self.permissions_list:
            if per in permissions:
                permissions[per].append(aid)
            else:
                permissions[per] = [aid]

        for p in permissions:
            row = sorted(permissions[p])
            l.append([p] + list(map(lambda a: self.checkbox(a[0] in row, '-'.join([str(a[0]), p.replace(' ', '-')])), access_groups)))
        l.sort(key=lambda a: a[0])
        return l

    def checkbox(self, value, name):
        return {True: '&#x2713;', False: '&#x2718;'}[value]

    def _get_permissions(self):
        return [list(a) for a in users.AccessOperations().get_permissions()]

    def get_acc_groups(self):
        return users.AccessOperations().get_access_group()


permission_structure = re.compile('(\d)+-([0-9a-zA-Z_-]+)')


class EditPermissions(PermissionOverview):
    page_title = 'Edit Permissions'
    permission = 'edit permissions'

    def permission_table(self):
        return SecureForm(
            TableElement(*self.compile_the_list()), action=str(self.url.path)
        )

    def checkbox(self, value, name):
        return Checkbox(name=name, value=name, checked=value)

    def _process_post(self):
        new_perm = []
        for item in self.url.post:
            m = re.fullmatch(permission_structure, item)
            if m:
                g = m.groups()
                #print('assigning permission ' + ' '.join([g[1].replace('-', ' '), 'to', str(g[0])]))
                new_perm.append([int(g[0]), g[1].replace('-', ' ')])
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