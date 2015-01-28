from dyc.middleware import Handler
from dyc_modules.theming._breadcrumbs import attach_breadcrumbs
from dyc_modules.theming._theming import theme_dc_obj

__author__ = 'Justus Adam'
__version__ = '0.1'


class Middleware(Handler):
    def handle_view(self, view, dc_obj):
        if 'theme' in dc_obj.handler_options:
            if dc_obj.handler_options['theme'] is True:
                theme_dc_obj(dc_obj)
            elif isinstance(dc_obj.handler_options['theme'], str):
                theme_dc_obj(dc_obj, dc_obj.handler_options['theme'])
        if ('breadcrumbs' in dc_obj.handler_options
            and dc_obj.handler_options['breadcrumbs'] is True):
            attach_breadcrumbs(dc_obj)