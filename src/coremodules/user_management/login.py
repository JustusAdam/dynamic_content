from framework.html_elements import FormElement, TableElement, ContainerElement, Label, Input
from framework.base_handlers import ContentHandler, RedirectMixIn
from framework.page import Page

from .database_operations import UserOperations

__author__ = 'justusadam'


class LoginHandler(RedirectMixIn):

    def process_content(self):
        message = ''
        if self.is_post():
            message = ContainerElement('Your Login failed, please try again.', classes={'alert'})
        return Page(self._url, 'Login', ContainerElement(message,
            FormElement(
                TableElement(
                    [Label('Username', label_for='username'), Input(name='username', required=True)],
                    [Label('Password', label_for='password'), Input(input_type='password', required=True, name='password')]
                )
                , action='/login', classes={'login-form'})
        ))

    def process_post_query(self):
        if not self._url.post_query['username'] or not self._url.post_query['password']:
            raise ValueError
        username = self._url.post_query['username']
        password = self._url.post_query['password']
        ops = UserOperations()
        if ops.authenticate_user(username, password):
            self.redirect('/')