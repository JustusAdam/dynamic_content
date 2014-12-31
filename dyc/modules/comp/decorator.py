from dyc.core.mvc import model as _model
from dyc.modules.comp import regions
from dyc.util import config as _config, decorators

__author__ = 'justusadam'


@decorators.apply_to_type(_model.Model, apply_before=False, return_from_decorator=False)
def Regions(model):
    def theme_config(theme):
        return _config.read_config('themes/' + theme + '/config.json')

    def _regions(client, theme):

        config = theme_config(theme)['regions']
        r = []
        for region in config:
            r.append(regions.RegionHandler(region, config[region], theme, client))
        return r

    # check region flag

    region_flag = 'has_regions'
    region_flag_value = True

    if not hasattr(model, region_flag) or getattr(model, region_flag) != region_flag_value:

        if not 'no-commons' in model.decorator_attributes:
            for region in _regions(model.client, model.theme):
                model[region.name] = str(region.compile())

        setattr(model, region_flag, region_flag_value)

        #
        # class Regions:
        # def __init__(self, func):
        #         self.function = func
        #
        #     def __call__(self, model, *args, **kwargs):
        #         try:
        #             res = self.function(model, *args, **kwargs)
        #         except TypeError as e:
        #             for a in (model, ) + args:
        #                 print(type(a))
        #             print(self.function)
        #             raise e
        #         if not 'no-commons' in model.decorator_attributes:
        #             for region in self.regions(model.client, model.theme):
        #                 model[region.name] = str(region.compile())
        #         return res if res else 'page'
        #
        #     def regions(self, client, theme):
        #         config = self.theme_config(theme)['regions']
        #         r = []
        #         for region in config:
        #             r.append(RegionHandler(region, config[region], theme, client))
        #         return r
        #
        #     def theme_config(self, theme):
        #         if not hasattr(self, '_theme_config'):
        #             setattr(self, '_theme_config', read_config(self.get_theme_path(theme) + '/config.json'))
        #         return self._theme_config
        #
        #     def get_theme_path(self, theme):
        #         return 'themes/' + theme