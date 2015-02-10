"""Implementation of the formatter object that renders the template"""
import re
import sys

from framework.http import response
from ..component import Component
from . import evaluator
from framework.includes import get_settings


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
    """
    Handler Object parsing the view name returned by the controller and
    compiling an appropriate response object.
    """

    def __init__(self):
        self.responses = {
            None: self.serve_document,
            'redirect': self.redirect
        }

    def __call__(self, view_name, dc_obj):
        c = ARG_REGEX.match(view_name) if view_name else None

        c, *arg = c.groups() if c else (None, view_name)

        handler = self.responses[c]

        return handler(dc_obj, *arg)

    @staticmethod
    def redirect(dc_obj, location):
        """
        Handle a redirect response

        :param dc_obj: the DynamicContent instance
        :param location: location to redirect to
        :return: response.Redirect()
        """
        return response.Redirect(
            location=location,
            headers=dc_obj.config.get('headers', None),
            cookies=dc_obj.config.get('cookies', None)
            )

    def serve_document(self, dc_obj, view_name):
        """
        Handle a 200 OK response

        :param dc_obj: the DynamicContent instance
        :param view_name: name of the view to use as template
        :return: response.Response()
        """

        encoding = dc_obj.config.get('encoding', _defaults['encoding'])
        decorator_attributes = dc_obj.config.get('decorator_attributes', {})

        if 'no-encode' in decorator_attributes:
            document = dc_obj.context['content']

        elif ('no_view' in decorator_attributes
              or view_name is None):
            document = dc_obj.context['content'].encode(encoding)
        else:
            pairing = self.make_pairing(dc_obj)
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
    def make_pairing(dc_obj):
        """
        Construct initial globals for template

        :param dc_obj: the DynamicContent instance
        :return: globals dict
        """
        return dict(
            dc_obj.context,
            request=dc_obj.request
        )

    @staticmethod
    def view_path(view, dc_obj):
        """
        Generator of paths in which to look for the template

        :param view: name of the view
        :param dc_obj: DynamicContent instance
        :return: generator of paths
        """
        view = view if view.endswith('.html') else view + '.html'
        if view.startswith('/'):
            yield view[1:]
        else:
            if 'template_directory' in dc_obj.config:
                yield dc_obj.config['template_directory'] + '/' + view

            yield get_settings().get('project_dir', '.') + '/templates/' + view
            yield get_settings()['dc_basedir'] + '/templates/' + view
