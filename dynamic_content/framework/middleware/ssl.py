"""SSL related middleware"""

from . import _infrastructure
from framework.http import ssl


class ConditionalRedirect(_infrastructure.Handler):
    """Redirect to ssl page if required by the view"""

    def handle_controller(self, dc_obj, handler, args, kwargs):
        """
        Overwriting parent method

        :param dc_obj:
        :param handler:
        :param args:
        :param kwargs:
        :return: Redirect or None
        """
        if dc_obj.request.ssl_enabled is True:
            return None
        if handler.options.get('require_ssl', False) is True:
            return ssl.conditional_redirect(dc_obj.request)
        return None
