from framework.singleton import singleton

__author__ = 'justusadam'


@singleton
class Modules:

    def __init__(self, modules):
        self._modules = modules

    def __getitem__(self, item):
        return self._modules[item]


    def __str__(self):
        return str(self._modules)