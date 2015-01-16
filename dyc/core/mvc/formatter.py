import re
import sys
import collections

from dyc.dchttp import response
from dyc.util import html, decorators, config
from .. import Component
from dyc import dchp


__author__ = 'Justus Adam'
__version__ = '0.2'


VAR_REGEX = re.compile("\{([\w_-]*?)\}")

ARG_REGEX = re.compile(":(\w+?):(.*)")

_defaults = {
    'theme': 'default_theme',
    'view': 'page',
    'content_type': 'text/html',
    'encoding': sys.getfilesystemencoding(),
}

_template_defaults = {
    'header': '',
    'sidebar_left': '',
    'sidebar_right': '',
    'editorial': '',
    'navigation': ''
}


@Component('TemplateFormatter')
class TemplateFormatter(object):

    responses = {
        None: 'serve_document',
        'redirect': 'redirect'
    }

    @decorators.multicache
    def theme_config(self, theme):
        return config.read_config('themes/{}/config.json'.format(theme))

    def __call__(self, view_name, model, request):

        c = ARG_REGEX.match(view_name) if view_name else None

        c, *arg = c.groups() if c else (None, view_name)

        handler = getattr(self, self.responses[c])

        return handler(model, request, *arg)

    def redirect(self, model, request, location):
        return response.Redirect(
            location=location,
            headers=model.headers,
            cookies=model.cookies
            )

    def serve_document(self, model, request, view_name):
        theme = model.theme if model.theme else _defaults['theme']
        encoding = (
            model.encoding
            if hasattr(model, 'encoding')
            and model.encoding
            else _defaults['encoding'])

        if 'no-encode' in model.decorator_attributes:
            document = model['content']

        elif ('no_view' in model.decorator_attributes
            or view_name is None):
            document = model['content'].encode(encoding)
        else:
            pairing = self.initial_pairing(model, theme, request)
            pairing['request'] = request
            file = open(self.view_path(view_name, model)).read()
            document = str(dchp.evaluator.evaluate_html(file, dict(pairing)))
            document = document.encode(encoding)

        return response.Response(document, 200, model.headers, model.cookies)

    @staticmethod
    def view_path(view, model):
        return view if '/' in view else ((
            model.template_directory
            if hasattr(model, 'template_directory')
            and model.template_directory
            else 'custom/template') + '/' + (
            view
            if view.endswith('.html')
            else view + '.html')
            )

    def _get_my_folder(self):
        return sys.modules[self.__class__.__module__].__file__.rsplit('/', 1)[0]

    def _get_config_folder(self):
        return self._get_my_folder()




