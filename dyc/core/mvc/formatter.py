import re
import sys

from dyc.dchttp import response
from .. import Component
from dyc import dchp


__author__ = 'Justus Adam'
__version__ = '0.3'


VAR_REGEX = re.compile("\{([\w_-]*?)\}")

ARG_REGEX = re.compile(":(\w+?):(.*)")

_defaults = {
    'theme': 'default_theme',
    'view': 'page',
    'content_type': 'text/html',
    'encoding': sys.getfilesystemencoding(),
}


@Component('TemplateFormatter')
class TemplateFormatter(object):

    responses = {
        None: 'serve_document',
        'redirect': 'redirect'
    }

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
            pairing = dict(model)
            pairing['request'] = request
            for path in self.view_path(view_name, model):
                try:
                    with open(path) as file:
                        string = file.read()
                        break
                except IOError:
                    continue
            else:
                raise IOError(view_name)

            document = str(dchp.evaluator.evaluate_html(string, dict(pairing)))
            document = document.encode(encoding)

        return response.Response(document, 200, model.headers, model.cookies)

    @staticmethod
    def view_path(view, model):
        view = view if view.endswith('.html') else view + '.html'
        if view.startswith('/'):
            yield view[1:]
        else:
            if hasattr(model, 'template_directory'):
                yield model.template_directory + '/' + view

            yield 'custom/template/' + view
            yield 'templates/' + view