"""
Hooking implementation
"""
from .machinery import component
from .errors import exceptions
from .includes import log

__author__ = 'Justus Adam'
__version__ = '0.1'


class Hook:
    """
    Abstract Hook baseclass. Used mainly to ensure typesafety
     in the Hook manager

    It is not recommended to directly subclass this class,
     subclass from InstanceHook or ClassHook instead,
     depending on the purpose you'll want to use the hook for.
    """
    __slots__ = 'priority',

    def __init__(self, priority=0):
        self.priority = priority

    def init_hook(self):
        raise NotImplementedError

    def is_initialized(self):
        raise NotImplementedError

    def register_instance(self):
        HookManager.manager().register(self.hook_name, self)

    @staticmethod
    def manager():
        return HookManager.manager()

    def get_hooks(self):
        raise NotImplementedError

    def blank_call_hooks(self, *args,**kwargs):
        raise NotImplementedError

    def blank_call_hooks_with(self, executable, *args, **kwargs):
        raise NotImplementedError

    def return_call_hooks(self, *args,**kwargs):
        raise NotImplementedError

    def return_call_hooks_with(self, executable, *args, **kwargs):
        raise NotImplementedError

    def yield_call_hooks(self, *args,**kwargs):
        raise NotImplementedError

    def yield_call_hooks_with(self, executable, *args, **kwargs):
        raise NotImplementedError


class ClassHook(Hook):
    """
    Base class for inheritance based hooks.

    Use by subclassing this class and setting the hook_name attribute,
     as well as implementing any additional methods you'd like

    The convenience methods (like is_initialized() or return_call_hooks())
     are all classmethods for class hooks such as this.

    Class hooks can be registered using the @register decorator.

    Additionally this type provides a register_class() method
     which can be used to register a new instance of this hook
     with the manager, but only if the constructor does not require
     additional arguments
    """
    __slots__ = ()
    hook_name = ''

    @classmethod
    def init_hook(cls):
        cls.manager().init_hook(cls.hook_name, cls)

    @classmethod
    def is_initialized(cls):
        return cls.manager().has_hook(cls.hook_name)

    @classmethod
    def register_class(cls, priority=0):
        cls(priority).register_instance()

    @classmethod
    def get_hooks(cls):
        return cls.manager().get_hooks(cls.hook_name)

    @classmethod
    def blank_call_hooks(cls, *args,**kwargs):
        cls.manager().blank_call_hooks(cls.hook_name, *args, **kwargs)

    @classmethod
    def blank_call_hooks_with(cls, executable, *args, **kwargs):
        cls.manager().blank_call_hooks(cls.hook_name, executable, *args, **kwargs)

    @classmethod
    def return_call_hooks(cls, *args,**kwargs):
        return cls.manager().return_call_hooks(cls.hook_name, *args, **kwargs)

    @classmethod
    def return_call_hooks_with(cls, executable, *args, **kwargs):
        return cls.manager().return_call_hooks_with(cls.hook_name, executable, *args, **kwargs)

    @classmethod
    def yield_call_hooks(cls, *args,**kwargs):
        return cls.manager().yield_call_hooks(cls.hook_name, *args,**kwargs)

    @classmethod
    def yield_call_hooks_with(cls, executable, *args, **kwargs):
        return cls.manager().yield_call_hooks_with(cls.hook_name, executable, *args, **kwargs)


class InstanceHook(Hook):
    __doc__ = """
    Instance based Hook type.

    Used by instantiating and then registering the instances.

    You'll first have to subclass this and implement any method you require
     when actually calling the hook.

    Useful if one wants to register the same hook type for multiple hooks
     or do runtime dynamic hook assignment.
    """
    __slots__ = 'hook_name',

    def __init__(self, hook_name, priority=0):
        self.hook_name = hook_name
        super().__init__(priority)

    def init_hook(self, expected_class=None):
        if expected_class is None:
            expected_class = self.__class__
        self.manager().init_hook(self.hook_name, expected_class)

    def is_initialized(self):
        return self.manager().has_hook(self.hook_name)

    def get_hooks(self):
        return self.manager().get_hooks(self.hook_name)

    def blank_call_hooks(self, *args,**kwargs):
        self.manager().blank_call_hooks(self.hook_name, *args, **kwargs)

    def blank_call_hooks_with(self, executable, *args, **kwargs):
        self.manager().blank_call_hooks(self.hook_name, executable, *args, **kwargs)

    def return_call_hooks(self, *args,**kwargs):
        return self.manager().return_call_hooks(self.hook_name, *args, **kwargs)

    def return_call_hooks_with(self, executable, *args, **kwargs):
        return self.manager().return_call_hooks_with(self.hook_name, executable, *args, **kwargs)

    def yield_call_hooks(self, *args,**kwargs):
        return self.manager().yield_call_hooks(self.hook_name, *args,**kwargs)

    def yield_call_hooks_with(self, executable, *args, **kwargs):
        return self.manager().yield_call_hooks_with(self.hook_name, executable, *args, **kwargs)


class FunctionHook(InstanceHook):
    """
    Special subclass of InstanceHook.

    Designed to allow you to quickly turn an arbitrary callable into a hook.

    Use by instantiating with the hook_name and a callable (function).

    Can also be created using the
     @function_hook(hook_name, priority, expected_class) decorator.
    """
    __slots__ = 'function',

    def __init__(self, function, hook_name, priority=0):
        super().__init__(hook_name, priority)
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def init_hook(self, expected_class=None):
        self.manager().init_hook(self.hook_name, expected_class)

    @classmethod
    def make(cls, hook_name, priority, expected_class=None):
        if expected_class is None:
            expected_class = cls
        assert issubclass(cls, expected_class)
        def inner(func):
            f = cls(func, hook_name, priority)
            if not f.is_initialized():
                f.init_hook(expected_class)
            f.register_instance()
            return func
        return inner


class FormHook(FunctionHook):
     pass


class HookList(list):
    __slots__ = ('hooks', 'expected_class', 'name')

    def __init__(self, name, *hooks, expected_class=Hook):
        super().__init__(*hooks)
        self.name = name
        self.expected_class = expected_class

    def append(self, p_object):
        if not isinstance(p_object, self.expected_class):
            raise TypeError(
                'Expected instance of {} for hook handler for hook {}, '
                'got {}'.format(self.expected_class, self.name, type(p_object))
            )
        super().append(p_object)
        self._sort()

    def _sort(self):
        self.sort(key=lambda a: a.priority, reverse=True)

    def extend(self, iterable):
        super().extend(iterable)
        self._sort()


@component.Component('HookManager')
class HookManager:
    __slots__ = '_hooks',

    def __init__(self):
        self._hooks = {}

    @staticmethod
    def manager():
        """
        Get the manager component instance

        :return: HookManager instance
        """
        return component.get_component('HookManager').get()

    def init_hook(self, hook, expected_class=Hook):
        """
        Initialize a hook. This is the clean way to do it,
         where it'll register the hook name, initialize an
         empty hooks list and set an expected type/class.

        :param hook:
        :param expected_class:
        :return:
        """
        assert issubclass(expected_class, Hook)
        assert hook
        if hook in self._hooks:
            raise exceptions.HookExists(hook)
        self._hooks[hook] = HookList(hook, expected_class=expected_class)

    def register(self, hook, handler):
        """
        Register a new handler with the named hook

        :param hook: name of the hook to register for
        :param handler: handler object/function
        :return: None
        """
        if not hook in self._hooks:
            log.print_warning(
                'Assigning to uninitialized hook {}, '
                'assuming type {}'.format(hook, type(handler))
            )
            self.init_hook(hook, type(handler))
        container = self._hooks[hook]
        container.append(handler)

    def has_hook(self, hook):
        return hook in self._hooks

    def get_hooks(self, hook):
        """
        Get list of hooks registered at name 'hook'

        :param hook:
        :return:
        """
        if not self.has_hook(hook):
            raise exceptions.HookNotInitialized(hook)
        return self._hooks[hook]

    def blank_call_hooks(self, hook, *args,**kwargs):
        """
        Call each hook with args and kwargs

        :param hook: hook name
        :param args: args to call hooks with
        :param kwargs: kwargs to call hooks with
        :return: None
        """
        for h in self.get_hooks(hook):
            h(*args, **kwargs)

    def blank_call_hooks_with(self, hook, executable, *args, **kwargs):
        """
        Call executable with each hook once with args, kwargs

        :param hook: hook name
        :param executable: executable to call with hook
        :param args: args to call hook with
        :param kwargs: kwargs to call hook with
        :return: None
        """
        assert callable(executable)
        for h in self.get_hooks(hook):
            executable(h, *args, **kwargs)

    def return_call_hooks(self, hook, *args,**kwargs):
        """
        Call hooks, break and return if a hook does not return None

        :param hook: hook name
        :param args: args to call hook with
        :param kwargs: kwargs to call hook with
        :return: hook(*arsg, **kwargs) if not None
        """
        for res in self.yield_call_hooks(hook, *args, **kwargs):
            if not res is None:
                return res
        return None

    def return_call_hooks_with(self, hook, executable, *args, **kwargs):
        """
        Call executable on hooks, break and return if a call does not return None

        :param hook: hook name
        :param executable: executable to call
        :param args: args to call with
        :param kwargs: kwargs to call with
        :return: return executable(hook, *args, **kwargs) if not None
        """
        for res in self.yield_call_hooks_with(hook, executable, *args, **kwargs):
            if not res is None:
                return res
        return None

    def yield_call_hooks(self, hook, *args,**kwargs):
        """
        Call hooks with args, kwargs yielding results

        :param hook: hook name
        :param args: args to call hook with
        :param kwargs: kwargs to call hook with
        :return: hook(*args, **kwargs)
        """
        for h in self.get_hooks(hook):
            res = h(*args, **kwargs)
            if not res is None: yield res

    def yield_call_hooks_with(self, hook, executable, *args, **kwargs):
        """
        Call executable on hooks with args, kwargs yielding results

        intended usage:

        hook_class.method(hook_instance, *args, **kwargs)

        :param hook: hook name
        :param executable: executable to call on hook
        :param args: args to call hook with
        :param kwargs: kwargs to call hook with
        :return: executable(hook, *args, **kwargs)
        """
        assert callable(executable)
        for h in self.get_hooks(hook):
            res = executable(h, *args, **kwargs)
            if not res is None: yield res


def register(*args, **kwargs):
    def inner(cls):
        if not cls.is_initialized():
            cls.init_hook()
        cls(*args, **kwargs).register_instance()
        return cls
    return inner