from application.fragments import AppFragment
from .config import ApplicationConfig

__author__ = 'justusadam'


class Application(AppFragment):
    externals = {}
    shell = {}
    modules = None

    def __init__(self, config):
        assert isinstance(config, ApplicationConfig)
        super().__init__(config)
        self.load()

    def load(self):
        self.load_modules()

    def load_modules(self):
        pass

    def run(self):
        pass