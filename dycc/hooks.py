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
        assert hook != ''
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