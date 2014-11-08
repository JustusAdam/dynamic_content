from dynct.core import handlers
from dynct.modules.comp.html_elements import TableElement, ContainerElement
from .login import LOGOUT_BUTTON
from . import users

__author__ = 'justusadam'


class UserInformationCommon(handlers.common.Commons):
    source_table = 'user_management'

    def __init__(self, machine_name, show_title, access_type, client):
        super().__init__(machine_name, show_title, access_type, client)

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


class UserInformation(handlers.content.Content):
    permission = 'view other user info'
    page_title = 'User Information'

    def __init__(self, url, client):
        super().__init__(client)
        self.url = url
        if self.url.page_id == self.client.user:
            self.permission = 'view own user info'

    def process_content(self):
        (user_id, username, email, first_name, middle_name, last_name, date_created) = users.get_single_user(
            self.url.page_id)
        return ContainerElement(
            TableElement(
                ['UID', str(user_id)],
                ['Username', username],
                ['Email-Address', email],
                ['Full name', ' '.join([first_name, middle_name, last_name])],
                ['Account created', date_created],
                ['Access Group', users.acc_grp(user_id)]
            )
        )