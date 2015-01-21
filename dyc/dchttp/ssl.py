from . import response
from dyc.includes import settings

def conditional_redirect(request):
	if request.ssl_enabled is True:
		return None
	else:
		return response.Redirect(
			location='https://{}{}'.format(request.host, (':' + str(settings.SERVER.ssl_port)) if request.port else '', request.path),
			code=301
			)