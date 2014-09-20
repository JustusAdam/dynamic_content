from pathlib import Path

from framework.config_tools import read_config
from framework.html_elements import ContainerElement, Stylesheet, Script, LinkElement
from .regions import RegionHandler


__author__ = 'justusadam'


class ThemeHandler:

    def __init__(self, page):
        self._pattern = {}
        self.page = page
        self.module_config = read_config(self.get_my_folder() + '/config.json')
        self.used_theme = self.get_used_theme()
        self.theme_path = self.get_theme_path()
        self.theme_config = read_config(self.theme_path + '/config.json')

    def get_used_theme(self):
        if self.page.used_theme == 'active':
            return self.module_config['active_theme']
        elif self.page.used_theme == 'default':
            return self.module_config['default_theme']
        else:
            return self.page.used_theme

    def get_theme_path(self):
        return 'themes/' + self.used_theme

    def get_my_folder(self):
        return str(Path(__file__).parent)

    def compile_stylesheets(self):
        s = list(str(a) for a in self.page.stylesheets)
        if 'stylesheets' in self.theme_config:

            s += list(str(Stylesheet('/theme/' + self.module_config['active_theme'] + '/' + self.theme_config['stylesheet_directory'] + '/' + a)) for a in self.theme_config['stylesheets'])
        self._pattern['stylesheets'] = ''.join(s)
        return True

    def compile_scripts(self):
        s = list(str(a) for a in self.page.scripts)
        if 'scripts' in self.theme_config:
            s += list(str(Script(self.module_config['active_theme_path'] + '/' + self.theme_config['script_directory'] + '/' + a)) for a in self.theme_config['scripts'])
        self._pattern['scripts'] = ''.join(s)
        return True

    def compile_footer(self):
        self._pattern['footer'] = str(ContainerElement('_jaide CMS - &copy; Justus Adam 2014', element_id='powered_by'))
        return True

    def get_template_directory(self):
        path = self.module_config['active_theme_path']
        if 'template_directory' in self.theme_config:
            path += '/' + self.theme_config['template_directory']
        else:
            path += '/' + 'templates'
        return path + '/'

    def compile_meta(self):
        if 'favicon' in self.theme_config:
            favicon = self.theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        self._pattern['meta'] = LinkElement('/theme/' + self.used_theme + '/' + favicon, rel='shortcut icon', element_type='image/png')

    @property
    def regions(self):
        r = []
        for region in self.theme_config['regions']:
            r.append(RegionHandler(region, self.used_theme))
        return r

    @property
    def compiled(self):
        self.compile_scripts()
        self.compile_stylesheets()
        self.compile_meta()
        self._pattern['header'] = ''
        self.compile_footer()
        self._pattern['title'] = self.page.title
        self._pattern['content'] = str(self.page.content)
        self._pattern['pagetitle'] = ContainerElement('msaw - my super awesome website', html_type='a', additionals='href="/"')
        for region in self.regions:
            self._pattern[region.name] = str(region.compiled())

        template = open(self.get_template_directory() + 'page.html').read()
        return template.format(**self._pattern)