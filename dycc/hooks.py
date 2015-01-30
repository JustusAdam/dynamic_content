from . import Component, get_component
import collections
from dycc.errors import exceptions
from .util import console

__author__ = 'Justus Adam'
__version__ = '0.1'


HookFunc = collections.namedtuple('HookFunc', ('func', 'priority', 'class_'))
HookList = collections.namedtuple('HookList', ('hooks', 'expected_class'))


class Hook:
    hook_name = ''

    @classmethod
    def init_hook(cls):
        HookManager.manager().init_hook(cls.hook_name, cls)

    @classmethod
    def register_class(cls, priority=0):
        cls().register_instance(priority)

    def register_instance(self, priority=0):
        HookManager.manager().register(self.hook_name, self, priority)

    @staticmethod
    def manager():
        return HookManager.manager()

    @classmethod
    def get_hooks(cls):
        return cls.manager().get_hooks(cls.hook_name)


@Component('HookManager')
class HookManager:
    __slots__ = (
        '_hooks'
    )

    def __init__(self):
        self._hooks = {}

    @staticmethod
    def manager():
        """
        Get the manager component instance

        :return: HookManager instance
        """
        return get_component('HookManager')

    def init_hook(self, hook, expected_class=Hook):
        """
        Initialize a hook. This is the clean way to do it,
         where it'll register the hook name, initialize an
         empty hooks list and set an expected type/class.

        :param hook:
        :param expected_class:
        :return:
        """
        assert isinstance(expected_class, type)
        assert hook
        if hook in self._hooks:
            raise exceptions.HookExists(hook)
        self._hooks[hook] = HookList(hooks=[], expected_class=expected_class)

    def register(self, hook, handler, priority=0):
        """
        Register a new handler with the named hook

        :param hook: name of the hook to register for
        :param handler: handler object/function
        :param priority: where to place it in the list
        :return: None
        """
        if not hook in self:
            console.print_warning(
                'Assigning to uninitialized hook {}, '
                'assuming type {}'.format(hook, type(handler))
            )
            self._hooks[hook] = HookList(hooks=[], expected_class=type(handler))
        container = self._hooks[hook]
        if not isinstance(handler, container.expected_class):
            raise TypeError(
                'Expected instance of {} for hook handler for hook {}, '
                'got {}'.format(container.expected_class, hook, type(handler))
            )
        self._hooks[hook].append(handler)

    def get_hooks(self, hook):
        """
        Get list of hooks registered at name 'hook'

        :param hook:
        :return:
        """
        if not hook in self._hooks:
            raise exceptions.HookNotInitialized(hook)
        return self._hooks[hook].hooks

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