from . import Handler
from dyc.util import rest

__author__ = 'Justus Adam'
__version__ = '0.1'


class JSONTransform(Handler):
    def handle_view(self, view, dc_obj):
        if ('json_output' in dc_obj.handler_options
            and dc_obj.handler_options['json_output'] is True):
            return rest.json_response(view, dc_obj)
        return None