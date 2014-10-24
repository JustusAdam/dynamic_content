from modules.comp.regions import RegionHandler
from core.handlers.decorator import TemplateBasedDecorator


__author__ = 'justusadam'


class Decorator(TemplateBasedDecorator):
    template_name = 'page'

    def __init__(self, request, client, content):
        super().__init__(request, client, content)
        self._theme = content.theme

    @property
    def headers(self):
        headers = super().headers
        if self.content.headers:
            for header in self.content.headers:
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
        s = list(str(a) for a in self.content.scripts)
        return ''.join(s + [super().compile_scripts()])

    def compile_stylesheets(self):
        s = list(str(a) for a in self.content.stylesheets)
        return ''.join(s + [super().compile_stylesheets()])

    def compile_meta(self):
        s = list(str(a) for a in self.content.stylesheets)
        return ''.join(s + [super().compile_meta()])

    def _fill_template(self):
        self._template['title'] = self.content.title
        self._template['header'] = ''
        self._template['content'] = str(self.content.content)
        for region in self.regions:
            self._template[region.name] = str(region.compiled)
        super()._fill_template()