from framework.html_elements import FormElement, Input
from .database_operations import FormOperations

__author__ = 'justusadam'



class SecureForm(FormElement):

  def render_content(self):
    return super().render_content() + str(self.render_token())

  def render_token(self):
    token = FormOperations().new_token(self._customs['action'])
    return Input(input_type='hidden', name='form_token', value=token)