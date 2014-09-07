from pathlib import Path
from tools.config_tools import read_config
from .elements import ContainerElement, Stylesheet, Script

__author__ = 'justusadam'


class ThemeHandler:

    def __init__(self, page):
        self.page = page
        self.module_config = read_config(self.get_my_folder() + '/config.json')
        self.theme_path = self.get_theme_path()
        self.theme_config = read_config(self.theme_path + '/config.json')
        self._is_compiled = False
        self._document = None
        self._pattern = {}

    @property
    def document(self):
        if self._is_compiled:
            return self._document
        elif self.compile():
            return self._document
        else:
            return None

    def get_theme_path(self):
        if self.page.used_theme == 'active':
            return 'themes/' + self.module_config['active_theme']
        elif self.page.used_theme == 'default':
            return 'themes/' + self.module_config['default_theme']
        else:
            return 'themes/' + self.page.used_theme

    def get_my_folder(self):
        return str(Path(__file__).parent)

    def process_stylesheets(self):
        s = list(str(a) for a in self.page.stylesheets)
        if 'stylesheets' in self.theme_config:

            s += list(str(Stylesheet('/theme/' + self.module_config['active_theme'] + '/' + self.theme_config['stylesheet_directory'] + '/' + a)) for a in self.theme_config['stylesheets'])
        self._pattern['stylesheets'] = ''.join(s)
        return True

    def process_scripts(self):
        s = list(str(a) for a in self.page.scripts)
        if 'scripts' in self.theme_config:
            s += list(str(Script(self.module_config['active_theme_path'] + '/' + self.theme_config['script_directory'] + '/' + a)) for a in self.theme_config['scripts'])
        self._pattern['scripts'] = ''.join(s)
        return True

    def process_footer(self):
        self._pattern['footer'] = str(ContainerElement('Python CMS 2014', element_id='powered_by'))
        return True

    def get_template_directory(self):
        path = self.module_config['active_theme_path']
        if 'template_directory' in self.theme_config:
            path += '/' + self.theme_config['template_directory']
        else:
            path += '/' + 'templates'
        return path + '/'

    def compile(self):
        self.process_scripts()
        self.process_stylesheets()
        self._pattern['meta'] = ''
        self._pattern['header'] = ''
        self.process_footer()
        self._pattern['title'] = self.page.title
        self._pattern['content'] = str(self.page.content)
        self._pattern['pagetitle'] = 'Test'

        template = open(self.get_template_directory() + 'page.html').read()
        self._document = template.format(**self._pattern)

        self._is_compiled = True
        return True