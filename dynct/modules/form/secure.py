from dynct.modules.comp import html
from dynct.modules.form import tokens

__author__ = 'justusadam'


class SecureForm(html.FormElement):
    def render_content(self):
        return super().render_content() + str(self.render_token())

    def render_token(self):
        tid, token = tokens.new()
        return html.ContainerElement(
            html.Input(input_type='hidden', name=tokens._form_token_name, value=token), html.Input(input_type='hidden', name=tokens._form_identifier_name, value=tid)
        , additional={'style': 'display:none;'})