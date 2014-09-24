from framework.html_elements import FormElement, TableElement, ContainerElement, Label, Input
from framework.base_handlers import ContentHandler, RedirectMixIn
from framework.page import Page

from . import session

__author__ = 'justusadam'


class LoginHandler(ContentHandler, RedirectMixIn):

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
        username = self._url.post_query['username'][0]
        password = self._url.post_query['password'][0]
        token = session.start_session(username, password)
        if token:
            self.add_morsel(('SESS', token))
            self.redirect('/')