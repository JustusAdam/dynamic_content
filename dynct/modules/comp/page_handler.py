from dynct.modules.comp.regions import RegionHandler
from dynct.core.handlers.page import Page


__author__ = 'justusadam'


class DecoratorWithRegions(Page):
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

    def initial_pairing(self):
        if not 'no-commons' in self.model.decorator_attributes:
            for region in self.regions:
                self._model[region.name] = str(region.compile())
        return super().initial_pairing()