from dynct.modules.comp.regions import RegionHandler
from dynct.core.handlers.page import Page



__author__ = 'justusadam'


class BasicHandler(Page):
    _theme = None
    view_name = 'page'

    def __init__(self, model, url, client_info):
        super().__init__(model, url, client_info)

    @property
    def regions(self):
        config = self.theme_config['regions']
        r = []
        for region in config:
            r.append(RegionHandler(region, config[region], self.theme, self.client))
        return r

    def _fill_model(self):
        for region in self.regions:
            self._model[region.name] = str(region.compiled)
        super()._fill_model()