"""Implementation of the scanner object and its parts and hooks"""
import collections
import importlib
import inspect
import logging
import pathlib

from framework import hooks, includes
from framework.machinery import linker, component

__author__ = 'Justus Adam'
__version__ = '0.1.2'


def submodules_from_path(
        current_module: pathlib.Path,
        parent_modules=tuple
):
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
                yield '.'.join(me)

                for path in contents:

                    # return submodules recursively
                    for submodule in submodules_from_path(path, me):
                        yield submodule
                break


def submodules_from_name(module, parents):
        path = pathlib.Path(
            # from the modules file
            importlib.import_module(
                (('.'.join(parents) + '.' + module)
                 if parents
                 else module)
            ).__file__
        )
        if path.name == '__init__.py':
            path = path.parent

        return tuple(
            submodule

            # we iterate over modules and apps
            # modules first

            # we get all submodules
            for submodule in submodules_from_path(
                # we construct paths first
                path,
                parents
            )
        )


class ScannerHook(hooks.ClassHook):
    """
    Hook into the module scanning to handle certain types or names of Symbols
    """
    __slots__ = ()
    hook_name = 'module_scan_hook'

    def __call__(self, module, var_name, var):
        raise NotImplementedError


ScannerHook.init_hook()


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
            res = hook(var)
            if inspect.isgenerator(res):
                for i in res:
                    yield i
            else:
                yield res

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
    def make(cls, *selectors):
        """
        Decorator function to register a new hook

        :param selectors: selectors the hook handles
        :return: wrapper func
        """
        def inner(executable):
            """
            Wrapper function for registering executable as hook
            :param executable: callable that handles the hook
            :return: unchanged executable
            """
            for selector in selectors:
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


@hooks.register()
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


@hooks.register()
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


@hooks.register()
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
    __slots__ = ('linker', 'hashable_tracker', 'unhashable_tracker')

    @component.inject_method(linker.Linker)
    def __init__(self, linker):
        self.linker = linker
        # the tracker will keep track of all scanned values
        # to avoid handling them twice
        self.hashable_tracker = set()
        self.unhashable_tracker = list()

    @component.inject_method(includes.SettingsDict)
    def scan_from_settings(self, settings):
        """
        Scan all modules defined as module or import in settings

        :param settings: injected settings
        :return: None
        """

        # we construct a list of modules
        # from the parent modules
        # mentioned in settings
        framework = ('framework', importlib.import_module('framework'))

        modules_from_settings = tuple(
            (module, importlib.import_module('dycm.{}'.format(module)))
            for module in settings.get('modules', ())
        )

        apps = tuple(
            (module, importlib.import_module(module))
            for module in settings.get('import', ())
        )

        modules = tuple(
            (framework,) + modules_from_settings + apps
        )

        self.scan(modules)

    def scan(self, modules):
        """
        Scan these modules for interesting objects
        :param modules:
        :return:
        """
        for name, module in modules:
            # we go through all the modules first and find all scanner hooks
            # so we can ensure all of them are present
            # at the start of the actual scan later
            for hook in self.find_scanner_hooks(module):
                logging.getLogger(__name__).debug(
                    'Found scanner hook {}'.format(hook)
                )
                if hook not in hook.get_hooks():
                    hook.register_instance()
                    logging.getLogger(__name__).debug(
                        'Hook registered'
                    )
                else:
                    logging.getLogger(__name__).debug(
                        'Hook discarded'
                    )

        for name, module in modules:
            # now we go through each module
            # calling the hooks we discovered earlier
            self.linker.init_module(
                name,
                (link for link in self.find_any(name, module))
            )
            logging.getLogger(__name__).debug(
                'Linking module {} with {}'.format(name, self.linker[name])
            )

    def find_any(self, module_name,  module):
        """
        Iter module and call hooks on each symbol

        :param module_name: name of the topmost parent module
        :param submodule: the module in question
        :return:
        """
        for var_name, var in self.iter_module_once(module):
            for links in ScannerHook.yield_call_hooks(module_name, var_name, var):
                for link in links:
                    if link is not None:
                        yield link

    def find_scanner_hooks(self, module):
        """
        Finds instances of ScannerHook and registers them

        :param module: module object
        :return:
        """
        for var_name, var in self.iter_module(module):
            if isinstance(var, ScannerHook):
                yield var

    def __contains__(self, item):
        return item in self.get_tracker(item)

    def get_tracker(self, item):
        """
        Return appropriate tracker, depending on
        whether the item is hashable or not

        :param item:
        :return:
        """
        try:
            hash(item)
            return self.hashable_tracker
        except TypeError:
            return self.unhashable_tracker

    def add(self, item):
        """
        Add an item

        :param item:
        :return:
        """
        if item not in self:
            try:
                hash(item)
                self.hashable_tracker.add(item)
            except TypeError:
                self.unhashable_tracker.append(item)

    def iter_module_once(self, module):
        """
        A custom generator to only return
        the symbols defined in the module once

        :param module: module object
        :return: yielding symbols/symbol names
        """
        for var_name, var in self.iter_module(module):
            if var not in self:
                self.add(var)
                yield var_name, var

    @staticmethod
    def iter_module(module):
        """
        Iterate through all public variables of a given module

        :param module:
        :return:
        """
        for var_name, var in vars(module).items():
            if var_name.startswith('_'):
                # we omit private/protected values
                continue
            yield var_name, var