from framework.html_elements import FormElement, TableElement, ContainerElement, Label, Input
from framework.base_handlers import ContentHandler

__author__ = 'justusadam'


class LoginHandler(ContentHandler):



    @property
    def compiled(self):
        return ContainerElement(
            FormElement(
                TableElement(
                    [Label('Username', label_for='username'), Input(name='username', required=True)],
                    [Label('Password', label_for='password'), Input(input_type='password', required=True, name='password')]
                )
            , action='/login', classes={'login-form'})
        )