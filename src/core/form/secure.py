from framework.html_elements import FormElement, Input, SubmitButton
from .database_operations import FormOperations

__author__ = 'justusadam'



class SecureForm(FormElement):

  def __init__(self, form_url, user, *content, action='{this}', classes=set(), element_id='', method='post', charset='UTF-8',
               submit=SubmitButton(), target='', additionals={}):
    super().__init__(content, action, classes, element_id, method, charset, submit, target, additionals)
    self.form = form_url
    self.user = user

  def render_content(self):
    return super().render_content() + self.render_token()

  def render_token(self):
    token = FormOperations().new_token(self.form, self. user)
    Input(input_type='hidden', name='form_token', value=token)