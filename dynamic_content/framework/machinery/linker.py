"""
Implementation and BaseClasses of dynamic
connections between framework an modules
"""

from . import component
from framework.errors import exceptions

__author__ = 'Justus Adam'
__version__ = '0.1'


class Link(object):
    """
    Represents a connection between some kind of handler defined in a module
    and the dynamic_content internal logic
    """
    __slots__ = 'is_linked', 'strict'

    def __init__(self, strict=False):
        self.is_linked = False
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


@component.component('linker')
class Linker(dict):
    """
    Container and utility class for links
    """
    __slots__ = ()

    def link(self, module):
        """
        Link all links in module

        :param module:
        :return: None
        """
        for link in self[module]:
            link.link()

    def unlink(self, module):
        """
        Unlink all links in module

        :param module:
        :return: None
        """
        for link in self[module]:
            link.unlink()