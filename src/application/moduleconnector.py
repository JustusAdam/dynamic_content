from application.fragments import AppFragment
from includes import log

__author__ = 'justusadam'


class Modules(dict):
    updated = False
    _hooks = {}

    def __init__(self, ignore_overwrite=True):
        super().__init__()
        self.ignore_module_overwrite = ignore_overwrite

    def __setitem__(self, key, value):
        assert isinstance(value, AppFragment)
        assert isinstance(key, str)
        if key in self:
            log.write_warning(segment='Modules', message='overwriting registered module ' + key)
            if not self.ignore_module_overwrite:
                raise KeyError
        dict.__setitem__(self, key, value)
        self.updated = True

    def get_config(self, item):
        return self[item].config

    @property
    def hooks(self):
        if not self._hooks or self.updated:
            self._register_hooks()
        return self._hooks

    def _register_hooks(self):
        acc = {}
        for item in self:
            if hasattr(self[item], 'hooks'):
                if not isinstance(self[item].hooks, dict):
                    continue
                for i in self[item].hooks:
                    if i in acc:
                        acc[i].append(self[item].hooks[i])
                    else:
                        acc[i] = [self[item].hooks[i]]
        self._hooks = acc

#
#
# class ModuleConnector(callable):
#     def __init__(self, moduleconf, module):
#         assert isinstance(moduleconf, ModuleConfig)
#         self.config = moduleconf
#         self.module = module
#
#     def call_hook(self, hook):
#         return self.config.hooks[hook]
#
#     def __call__(self, *args, **kwargs):
#         return self.module.call(*args, **kwargs)