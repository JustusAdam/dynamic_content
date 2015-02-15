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

        self.link_action()
        self.is_linked = True

    def link_action(self):
        """linking implementation"""
        raise NotImplementedError

    def unlink(self):
        """remove/halt/hide the connection, deactivate the handler"""
        if not self.is_linked:
            if self.strict:
                raise exceptions.IsNotLinked(self)
            else:
                return
        self.unlink_action()
        self.is_linked = False

    def unlink_action(self):
        """unlinking implementation"""
        raise NotImplementedError


@component.component('linker')
class Linker(dict):
    """
    Container and utility class for links
    """
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