from framework.html_elements import FormElement, Input, SubmitButton
from .database_operations import FormOperations

__author__ = 'justusadam'



class SecureForm(FormElement):

  def __init__(self, user, *content, action='{this}', classes=set(), element_id='', method='post', charset='UTF-8',
               submit=SubmitButton(), target='', additionals={}):
    super().__init__(*content, action=action, classes=classes, element_id=element_id, method=method, charset=charset, submit=submit, target=target, additionals=additionals)
    self.user = user

  def render_content(self):
    return super().render_content() + str(self.render_token())

  def render_token(self):
    token = FormOperations().new_token(self._customs['action'])
    return Input(input_type='hidden', name='form_token', value=token)