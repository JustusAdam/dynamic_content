from . import response
from framework.includes import inject_settings, log


@inject_settings
def conditional_redirect(settings, request):
    if request.ssl_enabled is True:
        return None
    elif not settings['https_enabled']:
        log.print_warning('Forced redirect to encrypted connection was '
                                'requested, but SSL is not enabled.')
        log.write_warning('Forced redirect to encrypted connection was '
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
