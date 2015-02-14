"""Server action related Hooks"""

from framework import hooks

__author__ = 'Justus Adam'
__version__ = '0.1'


class ServerHook(hooks.ClassHook):
    """Hook for actions around the time of the server start"""
    hook_name = 'server_start_hook'

    def pre_start(self):
        """
        Hook before then server start.
        :return:
        """
        raise NotImplementedError

    def post_start(self):
        """
        Hook immediately after server start
        :return:
        """
        raise NotImplementedError