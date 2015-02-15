"""Implementation of the scanner object and its parts and hooks"""
import collections

from framework import hooks
from framework.machinery import linker, component

__author__ = 'Justus Adam'
__version__ = '0.1'


class ScannerHook(hooks.ClassHook):
    """
    Hook into the module scanning to handle certain types or names of Symbols
    """
    __slots__ = ()
    hook_name = 'module_scan_hook'

    def __call__(self, module, var_name, var):
        raise NotImplementedError


class _SingleValueMultihook(ScannerHook):
    __slots__ = 'internal_hooks',

    def __init__(self):
        super().__init__()
        self.internal_hooks = collections.defaultdict(list)

    def get_instance(self, instance):
        return instance

    def __call__(self, module, var_name, var):
        pass

    def get_internal_hook_selector(self, var_name, var):
        raise NotImplementedError


class Scanner(object):
    """
    Scanner object to find important functions in hooks
    """
    @component.inject_method(linker.Linker)
    def __init__(self, linker):
        self.linker = linker

    def scan(self, modules):
        for module in modules:
            # we go through all the modules first and find all scanner hooks
            # so we can ensure all of them are present
            # at the start of the actual scan later
            self.find_scanner_hooks(module)
        for module in modules:
            # now we go through each module
            # calling the hooks we discovered earlier
            self.find_any(module)

    def find_any(self, module):
        """
        Iter module and call hooks on each symbol

        :param module: module object
        :return:
        """
        # we immediately create a frozenset to immutably assign the links
        self.linker[module] = frozenset(
            link
            for var_name, var in self.iter_module(module)
            for link in ScannerHook.yield_call_hooks(module, var_name, var)
        )

    def find_scanner_hooks(self, module):
        """
        Finds instances of ScannerHook and registers them

        :param module: module object
        :return:
        """
        for var_name, var in self.iter_module(module):
            if not isinstance(var, ScannerHook):
                continue
            elif var not in ScannerHook.get_hooks():
                var.register_instance()

    @staticmethod
    def iter_module(module):
        """
        A custom generator to only return
        the symbols newly defined in the module

        :param module: module object
        :return: yielding symbols/symbol names
        """
        file = module.__file__
        for var_name, var in vars(module):
            if not var.__file__ == file:
                yield var_name, var