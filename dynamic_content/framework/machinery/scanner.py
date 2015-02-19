"""Implementation of the scanner object and its parts and hooks"""
import collections
import importlib
import pathlib

from framework import hooks, includes
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
        """
        Another level of indirection

        Implemented as a flyweight object
        """
        __slots__ = 'selector', 'executable'

        def __init__(self, selector, executable):
            self.selector = selector
            self.executable = executable

        def __call__(self, *args, **kwargs):
            return self.executable(*args, **kwargs)

    def __init__(self):
        super().__init__()
        self.internal_hooks = collections.defaultdict(list)

    def __call__(self, module, var_name, var):
        selector = self.get_internal_hook_selector(var_name, var)
        for hook in self.get_internal_hooks(selector):
            yield hook(var)

    def get_internal_hooks(self, selector):
        """
        Allows override for hook retrieval

        :param selector: the key
        :return: list of hooks
        """
        return self.internal_hooks[selector]

    def get_internal_hook_selector(self, var_name, var):
        """
        Get a selector from the subclass

        :param var_name: variable name
        :param var: variable value
        :return: selector (some value derived from either var_name or var)
        """
        raise NotImplementedError

    def add(self, selector, executable):
        """
        Register a new executable to handle the selector in question

        :param selector: key
        :param executable: executable to register
        :return:
        """
        assert self.is_selector(selector)
        self.internal_hooks[selector].add(
            self.HookContainer(selector, executable)
        )

    def is_selector(self, selector):
        """
        Verify whether the selector has the correct type

        :param selector:
        :return:
        """
        raise NotImplementedError


class SingleNameMultiHook(_SingleValueMultiHook):
    """Hook for name based handling"""
    __slots__ = ()

    def get_internal_hook_selector(self, var_name, var):
        """
        Uses variable names for selection

        :param var_name:
        :param var:
        :return:
        """
        return var_name

    def is_selector(self, selector):
        """
        Verify the selector is a string

        :param selector:
        :return:
        """
        return isinstance(selector, str)


class SingleTypeMultiHook(_SingleValueMultiHook):
    """Hook for type based handling"""
    __slots__ = ()

    def get_internal_hook_selector(self, var_name, var):
        """
        We use type for selection

        :param var_name:
        :param var:
        :return:
        """
        return type(var)

    def is_selector(self, selector):
        """
        Verify the selector is actually a type
        :param selector:
        :return:
        """
        return isinstance(selector, type)


class SingleSubtypesMultiHook(_SingleValueMultiHook):
    """Hooks for types that allow subtypes"""
    __slots__ = ()

    def get_internal_hook_selector(self, var_name, var):
        """
        This subclass uses variable (sub)types

        :param var_name:
        :param var:
        :return:
        """
        return type(var)

    def get_internal_hooks(self, selector):
        """
        Yield all hooks registered for that type as well as
        any registered for super types of that type

        :param selector: the type of the object
        :returns: yielding hooks
        """
        for hook in self.internal_hooks[selector]:
            yield hook
        for cls in selector.__bases__:
            for hook in self.internal_hooks[cls]:
                yield hook

    def is_selector(self, selector):
        """
        Selectors have to be an instance of type

        :param selector:
        :return:
        """
        return isinstance(selector, type)


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

    @component.inject_method(includes.SettingsDict)
    def scan_from_settings(self, settings):
        """
        Scan all modules defined as module or import in settings

        :param settings: injected settings
        :return: None
        """

        def get_submodules(current_module: pathlib.Path, parent_modules=tuple):
            """
            Helper function for constructing the
            python module paths from directories

            :param current_module: pathlib.Path of the current module
            :param parent_modules: tuple of parent module names
            :return: own submodules or self if self is not a package/dir
            """
            me = parent_modules + (current_module.stem, )
            if (current_module.is_file()
                    and current_module.suffix == '.py'
                    # we omit 'private' or 'protected' .py files
                    # starting with '_'
                    and not current_module.name.startswith('_')):
                # we only yield ourselves if we are only a .py file
                yield '.'.join(me)
            elif current_module.is_dir():
                # constructing tuple because we iterate over it twice
                contents = tuple(current_module.iterdir())
                for path in contents:
                    # ensure we are a package
                    if path.name == '__init__.py':
                        # return the package itself
                        yield me
                        # return submodules recursively
                        for path in contents:
                            yield get_submodules(path, me)

        # ----------------------------------------------------------
        # the helper function ends
        # ----------------------------------------------------------

        # we construct a list of modules
        # from the parent modules
        # mentioned in settings
        modules = tuple(

            # we get all submodules
            get_submodules(
                # we construct paths first
                pathlib.Path(
                    # from the modules file
                    importlib.import_module(module).__file__
                ),
                # the parent modules are empty at this point
                ()
            )


            # we iterate over the keys we
            # have to retrieve from settings first
            #
            # modules come first, apps later

            for a in ('modules', 'import')  # outer loop


            # and get the names contained
            #
            # we return an empty tuple
            # if the key isn't set

            for module in settings.get(a, ())  # inner loop
        )

        self.scan(*modules)


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