from framework.util.html import ContainerElement

__author__ = 'Justus Adam'
__version__ = '0.1'


def error_message(code, message=''):
    assert isinstance(message, str)
    ERROR_MESSAGES = {
        401: ContainerElement(
            ContainerElement(
                'Sorry, but you are not authorized to access this site',
                html_type='h1'
            ), ContainerElement(
                message
            )
        )
    }
    return ERROR_MESSAGES[code]
