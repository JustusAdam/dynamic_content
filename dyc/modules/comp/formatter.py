import pathlib
import re
from dyc.util import decorators
import sys

from dyc.dchttp import response
from dyc.util import html
from dyc.util.config import read_config


__author__ = 'justusadam'

VAR_REGEX = re.compile("\{([\w_-]*?)\}")

ARG_REGEX = re.compile(":(\w+?):")

_default_theme = 'default_theme'
_default_view = 'page'
_default_content_type = 'text/html'
_default_encoding = sys.getfilesystemencoding()



class TemplateFormatter:
    @decorators.multicache
    def theme_config(self, theme):
        return read_config('themes/' + theme + '/config.json')

    def __call__(self, view_name, model, url):
        theme = model.theme if model.theme else _default_theme
        content_type = model.content_type if hasattr(model, 'content_type') and model.content_type else _default_content_type
        encoding = model.encoding if hasattr(model, 'encoding') and model.encoding else _default_encoding
        # self.module_config = read_config(self._get_config_folder() + '/config.json')
        # if 'active_theme' in self.module_config:
        # self._theme = self.module_config['active_theme']
        theme_config = self.theme_config(theme)

        c = ARG_REGEX.match(view_name) if view_name else None

        if 'no-encode' in model.decorator_attributes:
            document = model['content']

        if 'no_view' in model.decorator_attributes or view_name is None:
            document = model['content'].encode(encoding)
        else:
            pairing = self.initial_pairing()
            file = open(self.view_path(theme, view_name)).read()
            for a in VAR_REGEX.finditer(file):
                if a.group(1) not in pairing:
                    pairing.__setitem__(a.group(1), '')
            document = file.format(**{a: str(pairing[a]) for a in pairing})


        cookies = model.cookies

        if not c:
            code = 200
        else:
            b = c.group(1)
            code, body, headers = self._map.get(b, self.compile_body)(self, self._model.view.lstrip(':' + b + ':'))
        headers = model.headers
        r = response.Response(document, code, headers, cookies)
        for attr in ['content_type', 'encoding']:
            if hasattr(model, attr):
                setattr(r, attr, getattr(model, attr))
            return r

    def view_path(self, theme, view):
        return '/'.join(['', 'themes', theme, 'templates', view + '.html'])

    def redirect(self, attr):
        if not attr:
            attr = '/'
        body = None
        code = 301
        headers = self.headers
        headers.add(("Location", attr))
        return code, body, headers

    _map = {
        'redirect': redirect
    }

    @property
    def theme_path_alias(self):
        return '/theme/' + self.theme

    @property
    def headers(self):
        headers = set()
        if hasattr(self.model, 'headers') and self.model.headers:
            for header in self.model.headers:
                headers.add(header)
        return headers

    def _get_my_folder(self):
        return str(pathlib.Path(sys.modules[self.__class__.__module__].__file__).parent)

    def _get_config_folder(self):
        return self._get_my_folder()

    def compile_stylesheets(self):
        s = self._list_from_model('stylesheets')
        if 'stylesheets' in self.theme_config:
            s += list(html.Stylesheet(
                self.theme_path_alias + '/' + self.theme_config['stylesheet_directory'] + '/' + a) for
                      a
                      in self.theme_config['stylesheets'])
        return ''.join([str(a) for a in s])

    def _list_from_model(self, model,  ident):
        if ident in model:
            return model[ident]
        else:
            return []

    def compile_scripts(self):
        s = self._list_from_model('scripts')
        if 'scripts' in self.theme_config:
            s += list(
                html.Script(self.theme_path_alias + '/' + self.theme_config['script_directory'] + '/' + a) for
                a
                in self.theme_config['scripts'])
        return ''.join([str(a) for a in s])

    def compile_meta(self):
        if 'favicon' in self.theme_config:
            favicon = self.theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        return str(
            html.LinkElement('/theme/' + self.theme + '/' + favicon, rel='shortcut icon', element_type='image/png'))

    def initial_pairing(self) -> dict:
        a = self.model.copy()
        a.update({
            'scripts': self.compile_scripts(),
            'stylesheets': self.compile_stylesheets(),
            'meta': self.compile_meta()
        })
        a.setdefault('breadcrumbs', self.render_breadcrumbs())
        a.setdefault('pagetitle',
                     html.A('/', 'dynamic_content - fast, python and extensible'))
        a.setdefault('footer', str(
            html.ContainerElement(
                html.ContainerElement('\'dynamic_content\' CMS - &copy; Justus Adam 2014', html_type='p'),
                element_id='powered_by', classes={'common', 'copyright'})))
        return a

    def breadcrumb_separator(self):
        return '>>'

    def breacrumbs(self):
        path = self.url.path.split('/')
        yield 'home', '/'
        for i in range(1, len(path)):
            yield path[i], '/'.join(path[:i+1])

    def render_breadcrumbs(self):
        def acc():
            for (name, location) in self.breacrumbs():
                for i in [
                    html.ContainerElement(self.breadcrumb_separator(), html_type='span',
                                          classes={'breadcrumb-separator'}),
                    html.ContainerElement(name, html_type='a', classes={'breadcrumb'}, additional={'href': location})
                ]:
                    yield i

        return html.ContainerElement(*list(acc()), classes={'breadcrumbs'})

        #
        # class DecoratorWithRegions(TemplateFormatter):
        # _theme = None
        #     view_name = 'page'
        #
        #     def __init__(self, model, url, client_info):
        #         super().__init__(model, url, client_info)
        #
        #     @property
        #     def regions(self):
        #         config = self.theme_config['regions']
        #         r = []
        #         for region in config:
        #             r.append(RegionHandler(region, config[region], self.theme, self.client))
        #         return r
        #
        #     def initial_pairing(self):
        #         if not 'no-commons' in self.model.decorator_attributes:
        #             for region in self.regions:
        #                 self._model[region.name] = str(region.compile())
        #         return super().initial_pairing()