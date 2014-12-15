from dynct.core.mvc.content_compiler import Content
from dynct.modules.comp.html import TableElement, ContainerElement
from dynct.modules.commons.commons import Commons
from .login import LOGOUT_BUTTON
from . import users, model

__author__ = 'justusadam'


class UserInformationCommon(Commons):
    source_table = 'user_management'

    def get_content(self, name):
        return ContainerElement(
            TableElement(
                ('Username: ', self.get_username(self.client.user)),
                ('Access Group: ', self.client.access_group),
                ('Joined: ', self.get_date_joined(self.client.user))
            ), LOGOUT_BUTTON
        )

    def get_username(self, user):
        if user == users.GUEST:
            return 'Anonymous'
        return users.get_user(user).username

    def get_date_joined(self, user):
        if user == users.GUEST:
            return 'Not joined yet.'
        return users.get_user(user).date_created


class UserInformation(Content):
    permission = 'view other user info'
    page_title = 'User Information'

    def __init__(self, model, url):
        super().__init__(model)
        self.page_id = url.path[1]
        if self.page_id == self.client.user:
            self.permission = 'view own user info'

    def process_content(self):
        user = users.get_single_user(
            self.page_id)
        grp = model.AccessGroup.get(aid=user.access_group)
        return ContainerElement(
            TableElement(
                ['UID', str(user.uid)],
                ['Username', user.username],
                ['Email-Address', user.email_address],
                ['Full name', ' '.join([user.user_first_name, user.user_middle_name, user.user_last_name])],
                ['Account created', user.date_created],
                ['Access Group', str(grp.aid) + ' (' + grp.machine_name + ')']
            )
        )


class UsersOverview(Content):
    page_title = 'User Overview'
    permission = 'access users overview'
    theme = 'admin_theme'

    def __init__(self, model, url):
        super().__init__(model)
        self.url = url

    def process_content(self):
        if 'selection' in self.url.get_query:
            selection = self.url.get_query['selection'][0]
        else:
            selection = '0,50'
        all_users = users.get_info(selection)
        acc = [['UID', 'Username', 'Name (if provided)', 'Date created', 'Actions']]

        for user in all_users:
            acc.append([ContainerElement(str(user.uid), html_type='a', additional={'href': '/users/' + str(user.uid)}),
                        ContainerElement(user.username, html_type='a', additional={'href': '/users/' + str(user.uid)}),
                        ' '.join([user.user_first_name, user.user_middle_name, user.user_last_name]),
                        user.date_created,
                        ContainerElement('edit', html_type='a',
                                         additional={'href': '/users/' + str(user.uid) + '/edit'})])

        if len(acc) == 1 or acc == []:
            return ContainerElement(ContainerElement('It seems you do not have any users yet.',
                                                     additional={'style': 'padding:10px;text-align:center;'}),
                                    ContainerElement('Would you like to ', ContainerElement('create one', html_type='a',
                                                                                            additional={
                                                                                                'href': '/users/new',
                                                                                                'style': 'color:rgb(255, 199, 37);text-decoration:none;'}),
                                                     '?', additional={'style': 'padding:10px;'}), additional={
                    'style': 'padding:15px; text-align:center; background-color: cornflowerblue;color:white;border-radius:20px;font-size:20px;'})
        return TableElement(*acc, classes={'user-overview'})