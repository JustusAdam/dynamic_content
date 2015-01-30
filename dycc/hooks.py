from . import Component, get_component
import collections
from .util import console

__author__ = 'Justus Adam'
__version__ = '0.1'


HookFunc = collections.namedtuple('HookFunc', ('func', 'priority', 'class_'))
HookList = collections.namedtuple('HookList', ('hooks', 'expected_class'))


class Hook:
    hook_name = ''

    def register(self, priority=0):
        HookManager.manager().register(self.hook_name, self, priority)


@Component('HookManager')
class HookManager:
    __slots__ = (
        '_hooks'
    )
    def __init__(self):
        self._hooks = {}

    @staticmethod
    def manager():
        return get_component('HookManager')

    def init_hook(self, hook, expected_class=Hook):
        assert isinstance(expected_class, type)
        assert hook
        self._hooks[hook] = HookList(hooks=[], expected_class=expected_class)

    def register(self, hook, handler, priority=0):
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
        return self._hooks[hook].hooks

    def blank_call_hooks(self, hook, *args,**kwargs):
         for h in self.get_hooks(hook):
             h(*args, **kwargs)

    def blank_call_hooks_with(self, hook, executable, *args, **kwargs):
        for h in self.get_hooks(hook):
            executable(h, *args, **kwargs)

    def return_call_hooks(self, hook, *args,**kwargs):
         for res in self.yield_call_hooks(hook, *args, **kwargs):
             if not res is None:
                 return res

    def return_call_hooks_with(self, hook, executable, *args, **kwargs):
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
        for h in self.get_hooks(hook):
            res = executable(h, *args, **kwargs)
            if not res is None: yield res