"""SSL related infrastructure"""

import logging

from . import response
from framework import includes
from framework.machinery import component


@component.inject(includes.SettingsDict)
def conditional_redirect(settings, request):
    """
    Redirect the request to the ssl enabled server (if existent)

    :param settings: injected settings
    :param request: incoming request
    :return: Redirect or None
    """
    if request.ssl_enabled is True:
        return None
    elif not settings['https_enabled']:
        logging.getLogger(__name__).debug(
            'Forced redirect to encrypted connection was '
            'requested, but SSL is not enabled.')
        logging.getLogger(__name__).debug(
            'Forced redirect to encrypted connection was '
            'requested, but SSL is not enabled.')
        return None
    else:
        return response.Redirect(
            location='https://{}{}'.format(
                request.host,
                (':' + str(settings['server']['ssl_port'])) if request.port else '',
                request.path
                ),
            code=response.HttpResponseCodes.MovedPermanently
            )
