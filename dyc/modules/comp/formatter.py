import re
import sys
import collections

from dyc.dchttp import response
from dyc.util import html, decorators, config
from dyc import core
from dyc import dchp


__author__ = 'Justus Adam'

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


@core.Component('TemplateFormatter')
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
            file = open(self.view_path(theme, view_name)).read()
            # for a in VAR_REGEX.finditer(file):
            #     if a.group(1) not in pairing:
            #         pairing.__setitem__(a.group(1), '')
            # document = file.format(**pairing)
            document = str(dchp.evaluator.evaluate_html(file, dict(pairing)))
            document = document.encode(encoding)

        return response.Response(document, 200, model.headers, model.cookies)

    @staticmethod
    def view_path(theme, view):
        return 'themes/{}/template/{}.html'.format(theme, view)

    @staticmethod
    def theme_path_alias(theme):
        return '/theme/' + theme

    def _get_my_folder(self):
        return sys.modules[self.__class__.__module__].__file__.rsplit('/', 1)[0]

    def _get_config_folder(self):
        return self._get_my_folder()

    def compile_stylesheets(self, model, theme):
        theme_config = self.theme_config(theme)
        s = self._list_from_model(model, 'stylesheets')
        if 'stylesheets' in theme_config:
            s += list(html.Stylesheet(
                '/'.join((self.theme_path_alias(theme), theme_config['stylesheet_directory'], a))) for
                      a
                      in theme_config['stylesheets'])
        return ''.join(str(a) for a in s)

    @staticmethod
    def _list_from_model(model,  ident):
        if ident in model:
            return model[ident]
        else:
            return []

    def compile_scripts(self, model, theme):
        theme_config = self.theme_config(theme)
        s = self._list_from_model(model, 'scripts')
        if 'scripts' in theme_config:
            s += list(
                html.Script('/'.join((self.theme_path_alias(theme), theme_config['script_directory'], a))) for
                a
                in theme_config['scripts'])
        return ''.join(str(a) for a in s)

    def compile_meta(self, model, theme):
        theme_config = self.theme_config(theme)
        favicon = (theme_config['favicon']
            if 'favicon' in theme_config
            else 'favicon.icon')
        return str(
            html.LinkElement(
                '/theme/' + theme + '/' + favicon,
                rel='shortcut icon',
                element_type='image/png'))

    def initial_pairing(self, model, theme, url) -> collections.ChainMap:
        return collections.ChainMap(
            dict(
                model,
                scripts=self.compile_scripts(model, theme),
                stylesheets=self.compile_stylesheets(model, theme),
                meta=self.compile_meta(model, theme)
            ),
            dict(
                breadcrumbs=self.render_breadcrumbs(url),
                pagetitle=html.A('/',
                    'dynamic_content - fast, python and extensible'),
                footer=str(
                html.ContainerElement(
                    html.ContainerElement(
                        '\'dynamic_content\' CMS - &copy; Justus Adam 2014',
                        html_type='p'),
                    element_id='powered_by',
                    classes={'common', 'copyright'}))
            ),
            _template_defaults
        )



    breadcrumb_separator = '>>'

    @staticmethod
    def breadcrumbs(url):
        path = url.path.split('/')
        yield 'home', '/'
        for i in range(1, len(path)):
            yield path[i], '/'.join(path[:i+1])

    def render_breadcrumbs(self, url):
        def acc():
            for (name, location) in self.breadcrumbs(url):
                for i in (
                    html.ContainerElement(
                        self.breadcrumb_separator,
                        html_type='span',
                        classes={'breadcrumb-separator'}
                    ),
                    html.ContainerElement(
                        name,
                        html_type='a',
                        classes={'breadcrumb'},
                        additional={'href': location}
                    )
                ):
                    yield i

        return html.ContainerElement(*tuple(acc()), classes={'breadcrumbs'})
