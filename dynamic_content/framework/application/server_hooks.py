from framework import hooks

__author__ = 'Justus Adam'
__version__ = '0.1'



class ServerHook(hooks.ClassHook):
    hook_name = 'server_start_hook'

    def pre_start(self):
        raise NotImplementedError

    def post_start(self):
        raise NotImplementedError