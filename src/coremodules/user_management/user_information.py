from framework.base_handlers import CommonsHandler
from framework.html_elements import TableElement, ContainerElement
from .database_operations import UserOperations
from framework.cli_info import ANONYMOUS

__author__ = 'justusadam'


class UserInformationCommon(CommonsHandler):

    source_table = 'user_management'

    def __init__(self, machine_name, show_title, user, access_group):
        super().__init__(machine_name, show_title, user, access_group)
        self.ops = UserOperations()

    def get_content(self, name):
        return TableElement(
            ('Username: ', self.get_username(self.user)),
            ('Access Group: ', self.access_group)
        )

    def get_username(self, user):
        if user == ANONYMOUS:
            return 'Anonymous'
        return self.ops.get_username(user)