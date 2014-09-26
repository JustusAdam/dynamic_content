from pathlib import Path
from urllib.error import HTTPError
from core import Modules, database_operations
from core.database_operations import DBOperationError
from coremodules.theme_engine.regions import RegionHandler
from coremodules.theme_engine.template import Template
from framework.base_handlers import PageHandler
from framework.config_tools import read_config
from framework.html_elements import Stylesheet, Script, LinkElement, ContainerElement

__author__ = 'justusadam'


class ContentHandler:
    @property
    def compiled(self):
        return ''


class TemplateBasedContentHandler(ContentHandler):
    
    _theme = 'active'
    
    template_name = None
    
    def __init__(self):
        self._template = Template(self.get_template_path())
        self.module_config = read_config(self.get_config_folder() + '/config.json')
        self.theme_config = read_config(self.theme_path + '/config.json')

    def get_template_path(self):
        path = self.module_config['active_theme_path']
        if 'template_directory' in self.theme_config:
            path += '/' + self.theme_config['template_directory']
        else:
            path += '/' + 'templates'
        return path + '/' + self.template_name + '.html'

    def get_my_folder(self):
        return str(Path(__file__).parent)
    
    def get_config_folder(self):
        return self.get_my_folder()

    @property
    def theme(self):
        return self._theme

    @property
    def theme_path(self):
        return 'themes/' + self.theme

    @property
    def compiled(self):
        self.fill_template()
        return str(self._template)
    
    def fill_template(self):
        pass
    

class BasicPageHandler(PageHandler, TemplateBasedContentHandler):
    
    _theme = None
    
    template_name = 'page'
    
    def __init__(self, url, client_info):
        self.modules = Modules()
        self.content_handler = self.get_content_handler()
        super().__init__(url, client_info)
        
    @property
    def theme(self):
        if not self._theme:
            self._theme = self.get_used_theme(self.content_handler)
        return self._theme

    def get_content_handler(self):
        return self.get_content_handler_class()(self._url, self)

    def get_content_handler_class(self):
        try:
            handler_module = database_operations.ContentHandlers().get_by_prefix(self._url.page_type)
        except DBOperationError as error:
            print(error)
            raise HTTPError(self._url, 404, None, None, None)

        handler = self.modules[handler_module].content_handler
        return handler

    def get_theme_handler_class(self):
        return self.modules['theme_engine'].theme_handler

    def get_theme_handler(self, content_handler, client_info):
        return self.get_theme_handler_class()(content_handler, client_info)

    @property
    def headers(self):
        headers = super().headers
        if self.content_handler.headers:
            for header in self.content_handler.headers:
                headers.add(header)
        return headers

    def get_used_theme(self, handler):
        if handler.theme == 'active':
            return self.module_config['active_theme']
        elif handler.theme == 'default':
            return self.module_config['default_theme']
        else:
            return handler.theme

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
            r.append(RegionHandler(region, config[region], self.theme, self.client_info.user, self.client_info.access_group))
        return r

    def fill_template(self):
        page = self.content_handler.compiled
        self._template['scripts'] = self.compile_scripts(page)
        self._template['stylesheets'] = self.compile_stylesheets(page)
        self._template['meta'] = self.compile_meta(self.theme)
        self._template['header'] = ''
        self._template['content'] = str(page.content)
        self._template['pagetitle'] = ContainerElement('msaw - my super awesome website', html_type='a', additionals='href="/"')
        for region in self.regions:
            self._template[region.name] = str(region.compiled)