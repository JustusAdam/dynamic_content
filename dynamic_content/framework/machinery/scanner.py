from framework import hooks

__author__ = 'Justus Adam'
__version__ = '0.1'


class ScannerHook(hooks.ClassHook):
    """
    Hook into the module scanning to handle certain types or names of Symbols
    """
    hook_name = 'module_scan_hook'

    def __call__(self, var_name, var):
        raise NotImplementedError


class Scanner(object):
    """
    Scanner object to find important functions in hooks
    """
    def __call__(self, modules):
        pass