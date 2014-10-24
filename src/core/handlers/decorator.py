import sys

from core.handlers.base import ContentCompiler, TemplateBasedContentCompiler
from modules.comp.html_elements import Stylesheet, Script, LinkElement, ContainerElement
from util.config import read_config


__author__ = 'justusadam'


class Decorator(ContentCompiler):
    def __init__(self, request, client, content):
        super().__init__(request)
        self._client = client
        self.page_type = None
        self.content_type = 'text/html'
        self.encoding = sys.getfilesystemencoding()
        self.content = content

    @property
    def encoded(self):
        return str(self.compiled).encode(self.encoding)

    @property
    def client(self):
        return self._client


class TemplateBasedDecorator(Decorator, TemplateBasedContentCompiler):
    template_name = 'page'

    def __init__(self, request, client, content):
        super().__init__(request, client, content)
        self.module_config = read_config(self._get_config_folder() + '/config.json')
        if 'active_theme' in self.module_config:
            self._theme = self.module_config['active_theme']

    def compile_stylesheets(self):
        s = []
        if 'stylesheets' in self.theme_config:
            s += list(str(Stylesheet(
                self.theme_path_alias + '/' + self.theme_config['stylesheet_directory'] + '/' + a)) for
                      a
                      in self.theme_config['stylesheets'])
        return ''.join(s)

    def compile_scripts(self):
        s = []
        if 'scripts' in self.theme_config:
            s += list(
                str(Script(self.theme_path_alias + '/' + self.theme_config['script_directory'] + '/' + a)) for
                a
                in self.theme_config['scripts'])
        return ''.join(s)

    def compile_meta(self):
        if 'favicon' in self.theme_config:
            favicon = self.theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        return str(LinkElement('/theme/' + self.theme + '/' + favicon, rel='shortcut icon', element_type='image/png'))

    def _fill_template(self):
        self._template.assign_key_safe('scripts', self.compile_scripts())
        self._template.assign_key_safe('stylesheets', self.compile_stylesheets())
        self._template.assign_key_safe('meta', self.compile_meta())
        self._template.assign_key_safe('breadcrumbs', self.render_breadcrumbs())
        self._template.assign_key_safe('pagetitle',
                                       ContainerElement('dynamic_content - fast, python and extensible', html_type='a',
                                                        additionals='href="/"'))
        self._template.assign_key_safe('footer', str(
            ContainerElement(ContainerElement('\'dynamic_content\' CMS - &copy; Justus Adam 2014', html_type='p'),
                             element_id='powered_by', classes={'common', 'copyright'})))

    def breadcrumb_separator(self):
        return '>>'

    def breacrumbs(self):
        for i in range(len(self.request.path)):
            yield self.request.path[i], self.request.path.prt_to_str(0, i + 1)

    def render_breadcrumbs(self):
        acc = []
        for (name, location) in self.breacrumbs():
            acc.append(
                ContainerElement(self.breadcrumb_separator(), html_type='span', classes={'breadcrumb-separator'}))
            acc.append(ContainerElement(name, html_type='a', classes={'breadcrumb'}, additionals={'href': location}))
        return ContainerElement(*acc, classes={'breadcrumbs'})