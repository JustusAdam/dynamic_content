from dynct.modules.comp.html import FormElement, Input, ContainerElement
from dynct.modules.form import tokens

__author__ = 'justusadam'


class SecureForm(FormElement):
    def render_content(self):
        return super().render_content() + str(self.render_token())

    def render_token(self):
        tid, token = tokens.new()
        return ContainerElement(
            Input(input_type='hidden', name='form_token', value=token), Input(input_type='hidden', name='form_id', value=tid)
        , additional={'style': 'display:none;'})