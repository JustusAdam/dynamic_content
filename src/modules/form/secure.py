from modules.comp.html_elements import FormElement, Input
from modules.form import tokens

__author__ = 'justusadam'



class SecureForm(FormElement):

  def render_content(self):
    return super().render_content() + str(self.render_token())

  def render_token(self):
    token = tokens.new(self._customs['action'])
    return Input(input_type='hidden', name='form_token', value=token)