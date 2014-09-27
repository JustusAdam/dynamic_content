from core.base_handlers import CommonsHandler
from framework.html_elements import TableElement, ContainerElement
from .database_operations import UserOperations
from core.users.cli_info import ANONYMOUS
from .login import LOGOUT_BUTTON

__author__ = 'justusadam'


class UserInformationCommon(CommonsHandler):
  source_table = 'user_management'

  def __init__(self, machine_name, show_title, user, access_group):
    super().__init__(machine_name, show_title, user, access_group)
    self.ops = UserOperations()

  def get_content(self, name):
    return ContainerElement(
      TableElement(
        ('Username: ', self.get_username(self.user)),
        ('Access Group: ', self.access_group),
        ('Joined: ', self.get_date_joined(self.user))
      ), LOGOUT_BUTTON
    )

  def get_username(self, user):
    if user == ANONYMOUS:
      return 'Anonymous'
    return self.ops.get_username(user)

  def get_date_joined(self, user):
    if user == ANONYMOUS:
      return 'Not joined yet.'
    return str(self.ops.get_date_joined(user))