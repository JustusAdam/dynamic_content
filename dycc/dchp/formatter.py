import re
import sys

from dycc.http import response
from .. import Component
from . import evaluator
from dycc.includes import settings


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

    def __call__(self, view_name, dc_obj):
        request = dc_obj.request

        c = ARG_REGEX.match(view_name) if view_name else None

        c, *arg = c.groups() if c else (None, view_name)

        handler = getattr(self, self.responses[c])

        return handler(dc_obj, request, *arg)

    @staticmethod
    def redirect(dc_obj, request, location):
        return response.Redirect(
            location=location,
            headers=dc_obj.config.get('headers', None),
            cookies=dc_obj.config.get('cookies', None)
            )

    def serve_document(self, dc_obj, request, view_name):
        encoding = (
            dc_obj.config['encoding']
            if 'encoding' in dc_obj.config
            and dc_obj.config['encoding']
            else _defaults['encoding'])

        dc_obj.config.setdefault('decorator_attributes', {})

        if 'no-encode' in dc_obj.config['decorator_attributes']:
            document = dc_obj.context['content']

        elif ('no_view' in dc_obj.config['decorator_attributes']
            or view_name is None):
            document = dc_obj.context['content'].encode(encoding)
        else:
            pairing = dc_obj.context
            pairing['request'] = request
            for path in self.view_path(view_name, dc_obj):
                try:
                    with open(path) as file:
                        string = file.read()
                        break
                except IOError:
                    continue
            else:
                raise IOError(view_name)

            document = str(evaluator.evaluate_html(string, pairing))
            document = document.encode(encoding)

        return response.Response(
            body=document,
            code=200,
            headers=dc_obj.config.get('headers', None),
            cookies=dc_obj.config.get('cookies', None)
            )

    @staticmethod
    def view_path(view, dc_obj):
        view = view if view.endswith('.html') else view + '.html'
        if view.startswith('/'):
            yield view[1:]
        else:
            if 'template_directory' in dc_obj.config:
                yield dc_obj.config['template_directory'] + '/' + view

            yield settings.get('project_dir', '.') + '/templates/' + view
            yield settings['dc_basedir'] + '/templates/' + view
