from framework.base_handlers import CommonsHandler
from framework.html_elements import TableElement, ContainerElement
from .database_operations import UserOperations

__author__ = 'justusadam'


class UserInformationCommon(CommonsHandler):

    source_table = 'login'

    def __init__(self, machine_name, show_title, user, access_group):
        super().__init__(machine_name, show_title, user, access_group)
        self.ops = UserOperations()

    def get_content(self, name):
        return TableElement(
            ('Username: ', self.get_username(None)),
            ('Access Group: ', ''),
            ('Active since: ', '')
        )

    def get_username(self, user):
        return self.ops.get_username(user)