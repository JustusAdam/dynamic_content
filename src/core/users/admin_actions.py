from core.handlers import PageContent, RedirectMixIn
from framework.html_elements import TableElement, Input, ContainerElement
from core.form import SecureForm
from core.users import users

__author__ = 'justusadam'


class CreateUser(PageContent, RedirectMixIn):
  page_title = 'Create User'

  destination = '/'

  message = ''

  def process_content(self):
    if 'destination' in self.url.get_query:
      target_url = str(self.url)
    else:
      target_url = str(self.url) + '?destination=' + self.destination + ''
    return str(ContainerElement(
      '{message}',
      SecureForm(
        TableElement(
          ('Name', Input(name='last_name')),
          ('Firstname (optional)', Input(name='first_name')),
          ('Middle Name (optional)', Input(name='middle_name')),
          ('Username', Input(name='username')),
          ('Password', Input(name='password', input_type='password')),
          ('Confirm Password', Input(name='confirm-password', input_type='password')
          )
        ), action=target_url, element_id='admin_form'
      )
    )).format(message=self.message)

  def process_post(self):
    if self.url.post['confirm-password'] == self.url.post['password']:
      args = dict()
      for key in ['username', 'password', 'last_name', 'first_name', 'middle_name']:
        if key in self.url.post:
          args[key] = self.url.post[key][0]
      users.add_user(**args)
      self.redirect(str(self.url.path))
    self.message = ContainerElement('Your passwords did not match.', classes='alert')