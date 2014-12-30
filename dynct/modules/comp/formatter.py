import pathlib
import re
import sys

from dynct.dchttp import response
from dynct.util import html
from dynct.util.config import read_config


__author__ = 'justusadam'

VAR_REGEX = re.compile("\{([\w_-]*?)\}")

ARG_REGEX = re.compile(":(\w+?):")

_default_theme = 'default_theme'


class TemplateFormatter:
    def __init__(self, model, url):
        self._theme = _default_theme
        self.view_name = 'page'
        self.content_type = 'text/html'
        self.encoding = sys.getfilesystemencoding()
        self._url = url
        if hasattr(model, 'content_type') and model.content_type:
            self.content_type = model.content_type
        if hasattr(model, 'encoding') and model.encoding:
            self.encoding = model.encoding
        self._model = model
        # self.module_config = read_config(self._get_config_folder() + '/config.json')
        # if 'active_theme' in self.module_config:
        # self._theme = self.module_config['active_theme']
        self._theme = _default_theme
        self.theme_config = read_config(self.theme_path + '/config.json')

    def redirect(self, attr):
        if not attr:
            attr = '/'
        body = None
        code = 301
        headers = self.headers
        headers.add(("Location", attr))
        return code, body, headers

    def document(self):
        return 200, self.compile_body(self.model.view), self.headers

    _map = {
        'redirect': redirect
    }

    @property
    def url(self):
        return self._url

    def compile_body(self, view_name):
        if 'no-encode' in self.model.decorator_attributes:
            return self.model['content']
        if 'no_view' in self.model.decorator_attributes:
            content = self.model['content']
        else:
            pairing = self.initial_pairing()
            file = open(self.view_path(view_name)).read()
            for a in VAR_REGEX.finditer(file):
                if a.group(1) not in pairing:
                    pairing.__setitem__(a.group(1), '')
            content = file.format(**{a: str(pairing[a]) for a in pairing})
        if hasattr(self.model, 'encoding'):
            encoding = self.model.encoding
        else:
            encoding = self.encoding
        return content.encode(encoding)

    def compile_response(self):
        cookies = self.model.cookies
        c = ARG_REGEX.match(self._model.view)
        if not c:
            code, body, headers = self.document()
        else:
            b = c.group(1)
            code, body, headers = self._map.get(b, self.compile_body)(self, self._model.view.lstrip(':' + b + ':'))
        headers |= self.model.headers
        r = response.Response(body, code, headers, cookies)
        for attr in ['content_type', 'encoding']:
            if hasattr(self.model, attr):
                setattr(r, attr, getattr(self.model, attr))
        return r

    @property
    def client(self):
        return self._model.client

    @property
    def model(self):
        return self._model

    @property
    def theme(self):
        if hasattr(self._model, 'theme'):
            if self._model.theme:
                return self._model.theme
        return self._theme

    def view_path(self, name):
        return self.theme_path + '/template/' + name + '.html'

    @property
    def theme_path(self):
        return 'themes/' + self.theme

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

    def _list_from_model(self, ident):
        if ident in self.model:
            return self.model[ident]
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
        for i in range(len(self.url.path)):
            yield self.url.path[i], self.url.path.prt_to_str(0, i + 1)

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