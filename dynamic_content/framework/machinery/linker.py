"""
Implementation and BaseClasses of dynamic
connections between framework an modules
"""

from . import component
import logging
from framework.errors import exceptions

__author__ = 'Justus Adam'
__version__ = '0.1.1'


class Link(object):
    """
    Represents a connection between some kind of handler defined in a module
    and the dynamic_content internal logic
    """
    __slots__ = 'is_linked', 'strict', 'module'

    def __init__(self, module, strict=False):
        self.is_linked = False
        self.module = module
        self.strict = strict

    def link(self):
        """link the connection/activate the handler"""
        if self.is_linked:
            if self.strict:
                raise exceptions.IsLinked(self)
            else:
                return
        try:
            self.link_action()
        except Exception as e:
            raise exceptions.LinkingFailed(
                self, nested_exception=e
            )
        self.is_linked = True

    def link_action(self):
        """the actual work of the link action"""
        raise NotImplementedError

    def unlink(self):
        """remove/halt/hide the connection, deactivate the handler"""
        if not self.is_linked:
            if self.strict:
                raise exceptions.IsNotLinked(self)
            else:
                return
        try:
            self.unlink_action()
        except Exception as e:
            raise exceptions.UnlinkingFailed(
                self, nested_exception=e
            )
        self.is_linked = False

    def unlink_action(self):
        """the actual work of the unlink action"""
        raise NotImplementedError


class SimpleLink(Link):
    __slots__ = 'variable',

    def __init__(self, module, variable, strict=False):
        super().__init__(module, strict)
        self.variable = variable


@component.component('linker')
class Linker:
    """
    Container and utility class for links
    """
    __slots__ = '_inner_dict',

    def __init__(self):
        self._inner_dict = {}

    def init_module(self, module, links):
        """
        Alternative way of __setitem__ that casts to a frozenset

        :param module:
        :param links:
        :return:
        """
        self._inner_dict[module] = frozenset(links)

    def __getitem__(self, item):
        return self._inner_dict[item]

    def __contains__(self, item):
        return item in self._inner_dict

    def values(self):
        """
        Emulating dict methods
        :return:
        """
        return self._inner_dict.values()

    def keys(self):
        """
        Emulating dict methods
        :return:
        """
        return self._inner_dict.keys()

    def items(self):
        """
        Emulating dict methods
        :return:
        """
        return self._inner_dict.items()

    def __iter__(self):
        return self._inner_dict.__iter__()

    def link(self, module):
        """
        Link all links in module

        :param module:
        :return: None
        """
        logging.getLogger(__name__).debug(
            'Linking module {}'.format(module)
        )
        for link in self[module]:
            link.link()

    def unlink(self, module):
        """
        Unlink all links in module

        :param module:
        :return: None
        """
        logging.getLogger(__name__).debug(
            'Unlinking module {}'.format(module)
        )
        for link in self[module]:
            link.unlink()