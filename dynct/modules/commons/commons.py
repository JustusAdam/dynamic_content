from dynct.core.handlers.common import Commons
from . import ar

__author__ = 'justusadam'


class TextCommons(Commons):
    com_type = 'text'

    def __init__(self, machine_name, show_title, access_type, client):
        super().__init__(machine_name, show_title, access_type, client)

    def get_content(self, name):
        return ar.com(self.com_type).get(machine_name=name).content