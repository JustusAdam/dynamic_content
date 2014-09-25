from pathlib import Path

from framework.config_tools import read_config
from framework.html_elements import ContainerElement, Stylesheet, Script, LinkElement
from .regions import RegionHandler


__author__ = 'justusadam'


class ThemeHandler:

    def __init__(self, content_handler):
        self.content_handler = content_handler
        self._pattern = {}
        self.module_config = read_config(self.get_my_folder() + '/config.json')
        self.theme = self.get_used_theme(content_handler)
        self.theme_config = read_config(self.theme_path + '/config.json')

    def get_used_theme(self, handler):
        if handler.theme == 'active':
            return self.module_config['active_theme']
        elif handler.theme == 'default':
            return self.module_config['default_theme']
        else:
            return handler.theme

    @property
    def theme_path(self):
        return 'themes/' + self.theme

    def get_my_folder(self):
        return str(Path(__file__).parent)

    def compile_stylesheets(self, page):
        s = list(str(a) for a in page.stylesheets)
        if 'stylesheets' in self.theme_config:

            s += list(str(Stylesheet('/theme/' + self.module_config['active_theme'] + '/' + self.theme_config['stylesheet_directory'] + '/' + a)) for a in self.theme_config['stylesheets'])
        return ''.join(s)

    def compile_scripts(self, page):
        s = list(str(a) for a in page.scripts)
        if 'scripts' in self.theme_config:
            s += list(str(Script(self.module_config['active_theme_path'] + '/' + self.theme_config['script_directory'] + '/' + a)) for a in self.theme_config['scripts'])
        return ''.join(s)

    def get_template_directory(self):
        path = self.module_config['active_theme_path']
        if 'template_directory' in self.theme_config:
            path += '/' + self.theme_config['template_directory']
        else:
            path += '/' + 'templates'
        return path + '/'

    def compile_meta(self, theme):
        if 'favicon' in self.theme_config:
            favicon = self.theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        return LinkElement('/theme/' + theme + '/' + favicon, rel='shortcut icon', element_type='image/png')

    @property
    def regions(self):
        config = self.theme_config['regions']
        r = []
        for region in config:
            r.append(RegionHandler(region, config[region], self.theme))
        return r

    @property
    def compiled(self):
        page = self.content_handler.compiled
        self._pattern['scripts'] = self.compile_scripts(page)
        self._pattern['stylesheets'] = self.compile_stylesheets(page)
        self._pattern['meta'] = self.compile_meta(self.theme)
        self._pattern['header'] = ''
        self._pattern['title'] = page.title
        self._pattern['content'] = str(page.content)
        self._pattern['pagetitle'] = ContainerElement('msaw - my super awesome website', html_type='a', additionals='href="/"')
        for region in self.regions:
            self._pattern[region.name] = str(region.compiled)

        template = open(self.get_template_directory() + 'page.html').read()
        return template.format(**self._pattern)