from modules.comp.html_elements import ContainerElement

__author__ = 'justusadam'


def error_message(code, message=''):
  assert isinstance(message, str)
  ERROR_MESSAGES = {
    401 : ContainerElement(
      ContainerElement(
        'Sorry, but you are not authorized to access this site', html_type='h1'
      ), ContainerElement(
        message
      )
    )
  }
  return ERROR_MESSAGES[code]