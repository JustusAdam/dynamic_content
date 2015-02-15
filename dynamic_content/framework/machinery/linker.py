from . import component

__author__ = 'Justus Adam'
__version__ = '0.1'


class Link(object):
    """
    Represents a connection between some kind of handler defined in a module
    and the dynamic_content internal logic
    """
    def link(self):
        """link the connection/activate the handler"""
        raise NotImplementedError

    def unlink(self):
        """remove/halt/hide the connection, deactivate the handler"""
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