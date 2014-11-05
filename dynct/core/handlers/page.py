from pathlib import Path
import re
import sys

from dynct.modules.comp.html_elements import Stylesheet, Script, LinkElement, ContainerElement
from dynct.util.config import read_config
from dynct.http.response import Response


__author__ = 'justusadam'

VAR_REGEX = re.compile("\{([\w_-]*?)\}")

_default_theme = 'default_theme'


class Page:
    def __init__(self, model, url, client):
        self._theme = _default_theme
        self.view_name = 'page'
        self.content_type = 'text/html'
        self.encoding = sys.getfilesystemencoding()
        self._url = url
        self._client = client
        if hasattr(model, 'content_type') and model.content_type:
            self.content_type = model.content_type
        if hasattr(model, 'encoding') and model.encoding:
            self.encoding = model.encoding
        self._model = model
        self.module_config = read_config(self._get_config_folder() + '/config.json')
        if 'active_theme' in self.module_config:
            self._theme = self.module_config['active_theme']
        self.theme_config = read_config(self.theme_path + '/config.json')

    @property
    def url(self):
        return self._url

    @property
    def compiled(self):
        if 'no-view' in self.model.decorator_attributes:
            return self.model['content']
        self._fill_model()
        file = open(self.view_path).read()
        for a in VAR_REGEX.finditer(file):
            if a.group(1) not in self.model:
                dict.__setitem__(self.model, a.group(1), '')
        return file.format(**{a: str(self.model[a]) for a in self.model})

    @property
    def encoded(self):
        code = 200
        headers = self.model.headers
        cookies = self.model.cookies
        if self.model.view.startswith(':redirect:'):
            body = None
            code = 301
            headers.add(("Location", self.model.view.lstrip(':redirect:')))
        elif 'no-view' in self.model.decorator_attributes:
            body = self.model['content']
        else:
            body = str(self.compiled).encode(self.encoding)
        r = Response(body, code, headers, cookies)
        for attr in ['content_type', 'encoding']:
            if hasattr(self.model, attr):
                setattr(r, attr, getattr(self.model, attr))
        return r

    @property
    def client(self):
        return self._client

    @property
    def model(self):
        return self._model

    @property
    def theme(self):
        if hasattr(self._model, 'theme'):
            if self._model.theme:
                return self._model.theme
        return self._theme

    @property
    def view_path(self):
        return self.theme_path + '/template/' + self.model.view + '.html'

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
        return str(Path(sys.modules[self.__class__.__module__].__file__).parent)

    def _get_config_folder(self):
        return self._get_my_folder()

    def compile_stylesheets(self):
        s = self._list_from_model('stylesheets')
        if 'stylesheets' in self.theme_config:
            s += list(Stylesheet(
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
                Script(self.theme_path_alias + '/' + self.theme_config['script_directory'] + '/' + a) for
                a
                in self.theme_config['scripts'])
        return ''.join([str(a) for a in s])

    def compile_meta(self):
        if 'favicon' in self.theme_config:
            favicon = self.theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        return str(LinkElement('/theme/' + self.theme + '/' + favicon, rel='shortcut icon', element_type='image/png'))

    def _fill_model(self):
        self._model.assign_key_safe('scripts', self.compile_scripts())
        self._model.assign_key_safe('stylesheets', self.compile_stylesheets())
        self._model.assign_key_safe('meta', self.compile_meta())
        self._model.assign_key_safe('breadcrumbs', self.render_breadcrumbs())
        self._model.assign_key_safe('pagetitle',
                                    ContainerElement('dynamic_content - fast, python and extensible', html_type='a',
                                                     additionals={'href':'/'}))
        self._model.assign_key_safe('footer', str(
            ContainerElement(ContainerElement('\'dynamic_content\' CMS - &copy; Justus Adam 2014', html_type='p'),
                             element_id='powered_by', classes={'common', 'copyright'})))

    def breadcrumb_separator(self):
        return '>>'

    def breacrumbs(self):
        for i in range(len(self.url.path)):
            yield self.url.path[i], self.url.path.prt_to_str(0, i + 1)

    def render_breadcrumbs(self):
        acc = []
        for (name, location) in self.breacrumbs():
            acc.append(
                ContainerElement(self.breadcrumb_separator(), html_type='span', classes={'breadcrumb-separator'}))
            acc.append(ContainerElement(name, html_type='a', classes={'breadcrumb'}, additionals={'href': location}))
        return ContainerElement(*acc, classes={'breadcrumbs'})