from dynct.includes.bootstrap import DEFAULT_THEME
from dynct.modules.comp.regions import RegionHandler
from dynct.util.config import read_config

__author__ = 'justusadam'


class Config:
    pass


_default_theme = 'default_theme'


class Autoconf:
    _attributes = {
        'theme': (lambda a: isinstance(a, str) if a else DEFAULT_THEME, DEFAULT_THEME)
    }

    def __init__(self, arg1):
        self.arg1 = arg1
        self.function = None
        self.config = None

    def __call__(self, other_self, *args, **kwargs):
        if isinstance(self.arg1, Config):
            self.config = self.make_conf(self.arg1, other_self)
            self.function = other_self
            return self.wrap
        else:
            self.config = self.make_conf(Config(), other_self)
            self.function = self.arg1
            return self.wrap(other_self, *args, **kwargs)


    def wrap(self, other, model, *args, **kwargs):
        self.work_model(model)
        return self.function(other, model, *args, **kwargs)

    def work_model(self, model):
        pass

    def make_conf(self, conf, controller):
        for attr in self._attributes:
            if not hasattr(conf, attr):
                if hasattr(controller, attr):
                    setattr(conf, attr, self._attributes[attr][0](controller[attr]))
                else:
                    setattr(conf, attr, self._attributes[attr][1])
        return conf


class Regions:
    def __init__(self, func):
        self.function = func

    def __call__(self, other, model, *args, **kwargs):
        res = self.function(other, model, *args, **kwargs)
        if not 'no-commons' in model.decorator_attributes:
            for region in self.regions(model.client, model.theme):
                model[region.name] = str(region.compile())
        return res if res else 'page'

    def regions(self, client, theme):
        config = self.theme_config(theme)['regions']
        r = []
        for region in config:
            r.append(RegionHandler(region, config[region], theme, client))
        return r

    def theme_config(self, theme):
        if not hasattr(self, '_theme_config'):
            setattr(self, '_theme_config', read_config(self.get_theme_path(theme) + '/config.json'))
        return self._theme_config

    def get_theme_path(self, theme):
        return 'themes/' + theme