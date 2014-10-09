from core.handlers.content import Content
from core.handlers.base import RedirectMixIn
from framework.html_elements import TableElement, Input, ContainerElement, Label
from core.form import SecureForm
from core.users import users
from .user_information import UserInformation

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


class CreateUser(Content, RedirectMixIn):

  page_title = 'Create User'
  destination = '/'
  message = ''
  permission = 'edit user accounts'

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
    (user_id, username, email, first_name, middle_name, last_name, date_created) = users.get_single_user(self.url.page_id)
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
                  ContainerElement('edit', html_type='a', additionals={'href': '/users/' + str(user_id) + '/edit'})])
    if len(acc) == 1 or acc == []:
      return ContainerElement(ContainerElement('It seems you do not have any users yet.', additionals={'style': 'padding:10px;text-align:center;'}), ContainerElement('Would you like to ', ContainerElement('create one', html_type='a', additionals={'href': '/users/new', 'style': 'color:rgb(255, 199, 37);text-decoration:none;'}), '?', additionals={'style': 'padding:10px;'}), additionals={'style': 'padding:15px; text-align:center; background-color: cornflowerblue;color:white;border-radius:20px;font-size:20px;'})
    return TableElement(*acc, classes={'user-overview'})