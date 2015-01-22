from . import response
from dyc.includes import settings
from dyc.util import console
from dyc.includes import log


def conditional_redirect(request):
    if request.ssl_enabled is True:
        return None
    elif not settings.HTTPS_ENABLED:
        console.print_warning('Forced redirect to encrypted connection was requested, but SSL is not enabled.')
        log.write_warning('Forced redirect to encrypted connection was requested, but SSL is not enabled.')
        return None
    else:
        return response.Redirect(
            location='https://{}{}'.format(request.host, (':' + str(settings.SERVER.ssl_port)) if request.port else '', request.path),
            code=301
            )