from framework import hooks

__author__ = 'Justus Adam'
__version__ = '0.1'


class ScannerHook(hooks.ClassHook):
    hook_name = 'module_scan_hook'

    def __call__(self, var_name, var):
        raise NotImplementedError