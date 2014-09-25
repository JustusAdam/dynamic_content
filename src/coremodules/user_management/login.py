from coremodules.iris import database_operations
from framework.html_elements import FormElement, TableElement, ContainerElement, Label, Input
from framework.base_handlers import ContentHandler, RedirectMixIn, CommonsHandler
from framework.page import Page

from . import session

__author__ = 'justusadam'


USERNAME_INPUT = Label('Username', label_for='username'), Input(name='username', required=True)
PASSWORD_INPUT = Label('Password', label_for='password'), Input(input_type='password', required=True, name='password')


LOGIN_FORM = FormElement(
    TableElement(
        USERNAME_INPUT,
        PASSWORD_INPUT
    )
    , action='/login', classes={'login-form'}
)

LOGIN_COMMON = FormElement(
    ContainerElement(
        *USERNAME_INPUT + PASSWORD_INPUT
    )
    , action='/login', classes={'login-form'}
)


class LoginHandler(ContentHandler, RedirectMixIn):
    def __init__(self, url, parent_handler):
        super().__init__(url, parent_handler)
        self.message = ''

    def process_content(self):
        return Page(self._url, 'Login', ContainerElement(self.message, LOGIN_FORM))

    def process_post_query(self):
        if not self._url.post_query['username'] or not self._url.post_query['password']:
            raise ValueError
        username = self._url.post_query['username'][0]
        password = self._url.post_query['password'][0]
        token = session.start_session(username, password)
        if token:
            self.add_morsel({'SESS': token})
            self.redirect('/iris/1')
        self.message = ContainerElement('Your Login failed, please try again.', classes={'alert'})

    def get_page_information(self):
        ops = database_operations.Pages()
        (content_type, title) = ops.get_page_information(self._url.page_type, self._url.page_id)
        theme = ops.get_theme(content_type=content_type)
        return title, content_type, theme


class LoginCommonHandler(CommonsHandler):
    def get_content(self, name):
        return LOGIN_COMMON