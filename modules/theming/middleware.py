from dynamic_content.middleware import Handler
from dycm import file
from . import _theming, model, _breadcrumbs

__author__ = 'Justus Adam'
__version__ = '0.1'


class Middleware(Handler):
    def handle_view(self, view, dc_obj):
        if 'theme' in dc_obj.handler_options:
            if dc_obj.handler_options['theme'] is True:
                _theming.theme_dc_obj(dc_obj)
            elif isinstance(dc_obj.handler_options['theme'], str):
                _theming.theme_dc_obj(dc_obj, dc_obj.handler_options['theme'])
        if ('breadcrumbs' in dc_obj.handler_options
            and dc_obj.handler_options['breadcrumbs'] is True):
            _breadcrumbs.attach_breadcrumbs(dc_obj)


class FileHandler(Handler):
    def handle_request(self, request):
        if request.path.startswith('/theme') and not request.path.endswith('/'):
            theme, path = request.path.split('/', 3)[2:]
            return file.serve_from(request, path, model.Theme.get(machine_name=theme).path)
