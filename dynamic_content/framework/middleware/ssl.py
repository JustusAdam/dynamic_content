from . import _infrastructure
from dynamic_content.http import ssl


class ConditionalRedirect(_infrastructure.Handler):
	def handle_controller(self, dc_obj, handler, args, kwargs):
		if 'require_ssl' in handler.options:
			if handler.options['require_ssl'] is True:
				return ssl.conditional_redirect(dc_obj.request)
		return None
