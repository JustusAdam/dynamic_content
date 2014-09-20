"""
The Modules singleton.

Allows access to all activated modules via the module name without a need to separately import them.
Created at startup by core.module_operations.load_active_modules()

This procedure also ensures that, if modules are accessed via this structure, inactive modules cannot be accessed and
all active modules are imported at startup, thus import failure will be detected ahead of the server accepting requests
and removing .py files or altering them after the server starts *should* not compromise it being operational as all code
needed is loaded immediately at server start.
"""

from framework.singleton import singleton
from .module_operations import get_active_modules

__author__ = 'justusadam'


@singleton
class Modules:

    _modules = None

    def reload(self):
        self._modules = self.load()

    def load(self):
        return get_active_modules()

    def __getitem__(self, item):
        return self._modules[item]

    def __str__(self):
        return str(self._modules)