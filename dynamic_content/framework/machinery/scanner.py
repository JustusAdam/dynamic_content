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


class _SingleValueMultiHook(ScannerHook):
    __slots__ = 'internal_hooks',

    class HookContainer(object):
        __slots__ = 'selector', 'executable'

        def __init__(self, selector, executable):
            self.selector = selector
            self.executable = executable

        def __call__(self, *args, **kwargs):
            return self.executable(*args, **kwargs)

    def __init__(self):
        super().__init__()
        self.internal_hooks = collections.defaultdict(list)

    def get_instance(self, instance):
        return instance

    def __call__(self, module, var_name, var):
        selector = self.get_internal_hook_selector(var_name, var)
        for hook in self.internal_hooks[selector]:
            yield hook(var)

    def get_internal_hook_selector(self, var_name, var):
        """
        Get a selector from the subclass

        :param var_name: variable name
        :param var: variable value
        :return: selector (some value derived from either var_name or var)
        """
        raise NotImplementedError

    def add(self, selector, executable):
        self.internal_hooks[selector].add(
            self.HookContainer(selector, executable)
        )


class SingleNameMultiHook(_SingleValueMultiHook):
    """Hook for name based handling"""
    def get_internal_hook_selector(self, var_name, var):
        return var_name


class SingleTypeMultiHook(_SingleValueMultiHook):
    """Hook for type based handling"""
    def get_internal_hook_selector(self, var_name, var):
        return type(var)


class Scanner:
    """
    Scanner object to find important functions in hooks
    """
    __slots__ = ('linker', 'tracker')

    @component.inject_method(linker.Linker)
    def __init__(self, linker):
        self.linker = linker
        # the tracker will keep track of all scanned values
        # to avoid handling them twice
        self.tracker = set()

    def scan(self, modules):
        """
        Scan these modules for interesting objects
        :param modules:
        :return:
        """
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
            for links in ScannerHook.yield_call_hooks(module, var_name, var)
            for link in links
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

    def iter_module(self, module):
        """
        A custom generator to only return
        the symbols defined in the module once

        :param module: module object
        :return: yielding symbols/symbol names
        """
        for var_name, var in vars(module):
            if var not in self.tracker:
                self.tracker.add(var)
                yield var_name, var