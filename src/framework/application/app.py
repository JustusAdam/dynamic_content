from .config import ApplicationConfig

__author__ = 'justusadam'


class Application(object):

  externals = {}
  shell = {}
  modules = None

  def __init__(self, config):
    assert isinstance(config, ApplicationConfig)
    self.config = config
    self.load()

  def load(self):
    self.load_modules()

  def load_modules(self):
    pass

  def run(self):
    pass