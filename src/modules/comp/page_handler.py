from urllib.error import HTTPError

from core import Modules, database_operations
from core.database_operations import DBOperationError
from modules.comp.regions import RegionHandler
from core.handlers.page import TemplateBasedPage
from modules.comp.html_elements import ContainerElement


__author__ = 'justusadam'


class BasicHandler(TemplateBasedPage):
    _theme = None
    template_name = 'page'

    def __init__(self, url, client_info):
        self.modules = Modules()
        self.content_handler = self._get_content_handler(url, client_info)
        super().__init__(url, client_info)


    @property
    def theme(self):
        if not self._theme:
            self._theme = self._get_used_theme(self.content_handler)
        return self._theme

    def _get_content_handler(self, url, client):
        return self._get_content_handler_class(url)(url, client)

    def _get_content_handler_class(self, url):
        try:
            handler_module = database_operations.ContentHandlers().get_by_prefix(url.page_type)
        except DBOperationError as error:
            print(error)
            raise HTTPError(self._url, 404, None, None, None)

        handler = self.modules[handler_module].content_handler(url)
        return handler

    @property
    def headers(self):
        headers = super().headers
        if self.content_handler.headers:
            for header in self.content_handler.headers:
                headers.add(header)
        return headers

    def _get_used_theme(self, handler):
        if handler.theme == 'active':
            return self.module_config['active_theme']
        elif handler.theme == 'default':
            return self.module_config['default_theme']
        else:
            return handler.theme

    @property
    def regions(self):
        config = self.theme_config['regions']
        r = []
        for region in config:
            r.append(RegionHandler(region, config[region], self.theme, self.client))
        return r

    def compile_scripts(self):
        s = list(str(a) for a in self.page.scripts)
        return ''.join(s + [super().compile_scripts()])

    def compile_stylesheets(self):
        s = list(str(a) for a in self.page.stylesheets)
        return ''.join(s + [super().compile_stylesheets()])

    def compile_meta(self):
        s = list(str(a) for a in self.page.stylesheets)
        return ''.join(s + [super().compile_meta()])

    def _fill_template(self):
        self.page = self.content_handler.compiled
        self._template['title'] = self.page.title
        self._template['header'] = ''
        self._template['content'] = str(self.page.content)
        for region in self.regions:
            self._template[region.name] = str(region.compiled)
        super()._fill_template()