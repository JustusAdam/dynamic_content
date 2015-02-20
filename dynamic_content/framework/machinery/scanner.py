"""Implementation of the scanner object and its parts and hooks"""
import collections
import importlib
import pathlib

from framework import hooks, includes
from framework.machinery import linker, component

__author__ = 'Justus Adam'
__version__ = '0.1.2'


class ScannerHook(hooks.ClassHook):
    """
    Hook into the module scanning to handle certain types or names of Symbols
    """
    __slots__ = ()
    hook_name = 'module_scan_hook'

    def __call__(self, module, var_name, var):
        raise NotImplementedError


class __MultiHookBase(ScannerHook):
    # internal_hooks does not need a slot, since it is a class attribute
    __slots__ = ()

    internal_hooks = collections.defaultdict(list)

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

    def __call__(self, module, var_name, var):
        selector = self.get_internal_hook_selector(var_name, var)
        for hook in self.get_internal_hooks(selector):
            yield hook(var)

    @classmethod
    def get_internal_hooks(cls, selector):
        """
        Allows override for hook retrieval

        :param selector: the key
        :return: list of hooks
        """
        return cls.internal_hooks[selector]

    @classmethod
    def get_internal_hook_selector(cls, var_name, var):
        """
        Get a selector from the subclass

        :param var_name: variable name
        :param var: variable value
        :return: selector (some value derived from either var_name or var)
        """
        raise NotImplementedError

    @classmethod
    def add(cls, selector, executable):
        """
        Register a new executable to handle the selector in question

        :param selector: key
        :param executable: executable to register
        :return:
        """
        assert cls.is_selector(selector)
        assert callable(executable)
        cls.internal_hooks[selector].append(
            cls.HookContainer(selector, executable)
        )

    @classmethod
    def make(cls, selector):
        """
        Decorator function to register a new hook

        :param selector: selector the hook handles
        :return: wrapper func
        """
        def inner(executable):
            """
            Wrapper function for registering executable as hook
            :param executable: callable that handles the hook
            :return: unchanged executable
            """
            cls.add(selector, executable)
            return executable
        return inner

    @classmethod
    def is_selector(cls, selector):
        """
        Verify whether the selector has the correct type

        :param selector:
        :return:
        """
        raise NotImplementedError


class SingleNameHook(__MultiHookBase):
    """Hook for name based handling"""
    __slots__ = ()

    # we need to reinitialize this or we'd
    # use the internal_hooks of the parent class
    internal_hooks = collections.defaultdict(list)

    @classmethod
    def get_internal_hook_selector(cls, var_name, var):
        """
        Uses variable names for selection

        :param var_name:
        :param var:
        :return:
        """
        return var_name

    @classmethod
    def is_selector(cls, selector):
        """
        Verify the selector is a string

        :param selector:
        :return:
        """
        return isinstance(selector, str)


class SingleTypeHook(__MultiHookBase):
    """Hook for type based handling"""
    __slots__ = ()

    # we need to reinitialize this or we'd
    # use the internal_hooks of the parent class
    internal_hooks = collections.defaultdict(list)

    @classmethod
    def get_internal_hook_selector(cls, var_name, var):
        """
        We use type for selection

        :param var_name:
        :param var:
        :return:
        """
        return type(var)

    @classmethod
    def is_selector(cls, selector):
        """
        Verify the selector is actually a type
        :param selector:
        :return:
        """
        return isinstance(selector, type)


class SingleSubtypeHook(__MultiHookBase):
    """Hooks for types that allow subtypes"""
    __slots__ = ()

    # we need to reinitialize this or we'd
    # use the internal_hooks of the parent class
    internal_hooks = collections.defaultdict(list)

    @classmethod
    def get_internal_hook_selector(cls, var_name, var):
        """
        This subclass uses variable (sub)types

        :param var_name:
        :param var:
        :return:
        """
        return type(var)

    @classmethod
    def get_internal_hooks(cls, selector):
        """
        Yield all hooks registered for that type as well as
        any registered for super types of that type

        :param selector: the type of the object
        :returns: yielding hooks
        """
        for hook in cls.internal_hooks[selector]:
            yield hook
        for class_ in selector.__bases__:
            for hook in cls.internal_hooks[class_]:
                yield hook

    @classmethod
    def is_selector(cls, selector):
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

                # we yield ourselves if we are only a .py file
                yield '.'.join(me)

            elif current_module.is_dir():

                # constructing tuple because we iterate over it twice
                contents = tuple(current_module.iterdir())

                for path in contents:

                    # ensure we are a package
                    if path.name == '__init__.py':

                        # return the package itself
                        yield me

                        for path in contents:

                            # return submodules recursively
                            for submodule in get_submodules(path, me):
                                yield submodule
                        break

        def submodules_from_tuple(mtuple, parents):
            return tuple(
                submodule

                # we iterate over modules and apps
                # modules first
                for module in mtuple

                # we get all submodules
                for submodule in get_submodules(
                    # we construct paths first
                    pathlib.Path(
                        # from the modules file
                        importlib.import_module(
                            (('.'.join(parents) + '.' + module)
                             if parents
                             else module)
                        ).__file__
                    ),
                    # the parent modules are empty at this point
                    parents
                )
            )

        # ----------------------------------------------------------
        # the helper functions end
        # ----------------------------------------------------------

        # we construct a list of modules
        # from the parent modules
        # mentioned in settings
        framework = submodules_from_tuple(
            ('framework',), ()
        )


        modules_from_settings = submodules_from_tuple(
            settings.get('modules', ()), ('dycm',)
        )

        apps = submodules_from_tuple(
            settings.get('import', ()), ()
        )

        modules = tuple(
            importlib.import_module(module)
            for module in framework + modules_from_settings + apps
        )

        self.scan(modules)

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
        for var_name, var in vars(module).items():
            if var_name.startswith('_'):
                # we omit private/protected values
                continue
            if var not in self.tracker:
                self.tracker.add(var)
                yield var_name, var