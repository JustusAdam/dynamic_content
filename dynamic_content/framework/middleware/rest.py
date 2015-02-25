"""Transform output into json strings"""
from . import Handler
from framework.util import rest

__author__ = 'Justus Adam'
__version__ = '0.1'


class JSONTransform(Handler):
    """
    Middleware that checks if a handler wants to return json
    and builds the appropriate response
    """
    def handle_view(self, view, dc_obj):
        """
        Check if the view wants to return json

        :param view:
        :param dc_obj:
        :return:
        """
        if ('json_output' in dc_obj.handler_options
            and dc_obj.handler_options['json_output'] is True
        ):
            return rest.json_response(view, dc_obj)
        return None