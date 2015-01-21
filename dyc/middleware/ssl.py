from . import _infrastructure
from dyc.dchttp import ssl


class ConditionalSSLRedirect(_infrastructure.Handler):
	def handle_controller(self, request, handler, args, kwargs):
		if 'require_ssl' in handler.options:
			if handler.options['require_ssl'] == True:
				return ssl.conditional_redirect(request)
		return None