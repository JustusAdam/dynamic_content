from core.base_handlers import PageContentHandler, RedirectMixIn
from framework.html_elements import FormElement, TableElement, Input, ContainerElement
from coremodules.user_management import users

__author__ = 'justusadam'


class CreateUser(PageContentHandler, RedirectMixIn):
 page_title = 'Create User'

 destination = '/'

 message = ''

 def process_content(self):
  if 'destination' in self._url.get_query:
   target_url = str(self._url)
  else:
   target_url = str(self._url) + '?destination=' + self.destination + ''
  return str(ContainerElement(
   '{message}',
   FormElement(
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

 def process_post_query(self):
  if self._url.post_query['confirm-password'] == self._url.post_query['password']:
   args = dict()
   for key in ['username', 'password', 'last_name', 'first_name', 'middle_name']:
    if key in self._url.post_query:
     args[key] = self._url.post_query[key][0]
   users.add_user(**args)
   self.redirect(str(self._url.path))
  self.message = ContainerElement('Your passwords did not match.', classes='alert')