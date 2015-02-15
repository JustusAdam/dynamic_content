from framework import hooks
from framework.machinery import linker, component

__author__ = 'Justus Adam'
__version__ = '0.1'


class ScanHandler(object):
    """
    Baseclass for handlers interacting with the scanner
    """
    def __init__(self, module):
        self.module = module

    def __call__(self, var_name, var_type) -> linker.Link:
        raise NotImplementedError

    @classmethod
    def make(cls, priority=0):
        """
        Construct a ScannerHook with this as handler

        :param priority: priority of the resulting hook
        :return: ScannerHook instance
        """
        return ScannerHook(cls, priority)


class ScannerHook(hooks.ClassHook):
    """
    Hook into the module scanning to handle certain types or names of Symbols
    """
    hook_name = 'module_scan_hook'

    def __init__(self, handler_class, priority):
        self.handler_class = handler_class
        super().__init__(priority)

    @classmethod
    def make(cls, priority=0):
        """
        Decorator to turn a subclass of ScanHandler into a usable Hook

        :param priority: priority of the resulting hook
        :return: wrapper func
        """
        def wrap(class_):
            assert isinstance(class_, ScanHandler)
            return cls(class_, priority)
        return wrap

    def __call__(self, module):
        return self.handler_class(module)

    def __eq__(self, other):
        if isinstance(other, ScannerHook):
            return other.handler_class == self.handler_class

    def __hash__(self):
        return hash(self.handler_class)


class Scanner(object):
    """
    Scanner object to find important functions in hooks
    """
    @component.inject_method(linker.Linker)
    def __init__(self, linker):
        self.linker = linker

    def __call__(self, modules):
        for module in modules:
            # we go through all the modules first and find all scanner hooks
            # so we can ensure none of them are perhaps not
            # present when we use them later
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
            handler(var_name, var)
            # we iterate through the scanner hooks first
            # since this call yields newly created handlers every time
            for handler in ScannerHook.yield_call_hooks(module)
            # and then the variables since they do not
            # get created every time
            for var_name, var in self.iter_module(module)
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
            elif issubclass(var, ScanHandler):
                var = var.make()
            if var not in ScannerHook.get_hooks():
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