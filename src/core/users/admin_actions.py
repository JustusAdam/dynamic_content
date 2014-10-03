from core.handlers import PageContent, RedirectMixIn
from framework.html_elements import TableElement, Input, ContainerElement, Label
from core.form import SecureForm
from core.users import users

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
  'email-address': {
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
  ('Password', 'password'),
  ('Confirm Password', 'confirm-password')
]


class CreateUser(PageContent, RedirectMixIn):
  page_title = 'Create User'

  destination = '/'

  message = ''

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
      if name in _edit_user_form:
        b = Input(name=name, **_edit_user_form[name])
      else:
        b = Input(name=name)
      acc.append(Label(display_name, label_for=name), b)

    return SecureForm(
          TableElement(
            *acc
          ), action=self.target_url(), element_id='admin_form'
        )



  def process_post(self):
    if self.url.post['confirm-password'] == self.url.post['password']:
      args = dict()
      for key in ['username', 'password', 'last_name', 'first_name', 'middle_name']:
        if key in self.url.post:
          args[key] = self.url.post[key][0]
      self.action(**args)
      self.redirect(str(self.url.path))
    self.message = ContainerElement('Your passwords did not match.', classes='alert')

  def action(self, **kwargs):
    users.add_user(**kwargs)


class EditUser(CreateUser):
  page_title = 'Edit User'

  destination = '/'

  message = ''

  def action(self, **kwargs):
    users.edit_user(**kwargs)




class UsersOverview(PageContent):

  page_title = 'User Overview'

  def process_content(self):
    if 'selection' in self.url.get_query:
      selection = self.url.get_query['selection'][0]
    else:
      selection = '0,50'
    all_users = users.get_info(selection)
    acc = [['id', 'Username', 'Name (if provided)', 'Date created', 'Actions']]
    for (user_id, username, user_first_name, user_middle_name, user_last_name, date_created) in all_users:
      acc.append([str(user_id), username, ' '.join([user_first_name, user_middle_name, user_last_name]), date_created,
                  ContainerElement('edit', html_type='a', additionals={'href': '/users/' + str(user_id) + '/edit'})])
    return TableElement(*acc)